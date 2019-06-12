#![recursion_limit = "1024"]
#![feature(await_macro, async_await)]
use server::{
    amqp_utils, background_task::BackgroundTask, background_task_constants,
    background_task_delivery, datetime_utils, Result,
};
use tokio::await;
use tokio::prelude::*;

use lapin_futures::options::{BasicConsumeOptions, BasicQosOptions};
use lapin_futures::types::FieldTable;
use log::{error, info, trace};

async fn consume_tasks_real() -> Result<()> {
    use background_task_constants::*;
    let client = await!(amqp_utils::connect_to_broker())?;
    let mut channel = await!(client.create_channel())?;
    let (tasks_queue, future_tasks_queue) =
        await!(amqp_utils::init_background_job_queues(&mut channel))?;
    let count = future_tasks_queue.message_count();
    if count == 0 {
        info!("Initially scheduling the databases update task...");
        let ttl = datetime_utils::compute_ttl_for_time(
            DATABASES_UPDATE_HOUR,
            DATABASES_UPDATE_MINUTE,
            DATABASES_UPDATE_SECOND,
        );
        await!(background_task_delivery::perform_delivery_on(
            &mut channel,
            BackgroundTask::UpdateAreaDatabases,
            Some(ttl)
        ))?;
    }
    let opts = BasicQosOptions {
        ..Default::default()
    };
    await!(channel.basic_qos(1, opts))?;
    let mut consumer = await!(channel.basic_consume(
        &tasks_queue,
        "tasks_consumer",
        BasicConsumeOptions::default(),
        FieldTable::default()
    ))?;
    info!("Starting tasks consumption...");
    while let Some(msg) = await!(consumer.next()) {
        let msg = msg?;
        trace!("Received message: {:?}", msg);
        let task: BackgroundTask = serde_json::from_slice(&msg.data)?;
        await!(task.execute())?;
        await!(channel.basic_ack(msg.delivery_tag, false))?;
        if let Some((hour, minute, second)) = task.get_next_schedule_time() {
            let ttl = datetime_utils::compute_ttl_for_time(hour, minute, second);
            await!(background_task_delivery::perform_delivery_on(
                &mut channel,
                task,
                Some(ttl)
            ))?;
        }
    }
    await!(channel.close(0, "Normal shutdown"))?;
    Ok(())
}

async fn consume_tasks() {
    if let Err(e) = await!(consume_tasks_real()) {
        error!("Error during task consumption: {:?}", e);
    }
}

fn main() -> Result<()> {
    server::init_logging();
    let _dotenv_path = dotenv::dotenv()?;
    tokio::run_async(consume_tasks());
    Ok(())
}
