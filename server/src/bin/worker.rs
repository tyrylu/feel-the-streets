#![feature(await_macro, async_await, futures_api)]
use server::{amqp_utils, background_task::BackgroundTask, background_task_constants, background_task_delivery, datetime_utils, Result};
use tokio::await;
use tokio::prelude::*;

use lapin_futures::channel::BasicGetOptions;
use log::{debug, info, error};

async fn consume_tasks_real() -> Result<()> {
    use background_task_constants::*;
    let (client, handle) = await!(amqp_utils::connect_to_broker())?;
    let (_tasks_queue, future_tasks_queue) = await!(amqp_utils::init_background_job_queues(&client))?;
    let channel = await!(client.create_channel())?;
    let count = future_tasks_queue.message_count();
    if count == 0 {
        info!("Initially scheduling the databases update task...");
        let ttl = datetime_utils::compute_ttl_for_time(DATABASES_UPDATE_HOUR, DATABASES_UPDATE_MINUTE, DATABASES_UPDATE_SECOND);
        await!(background_task_delivery::perform_delivery_on(&channel, BackgroundTask::UpdateAreaDatabases, Some(ttl), false))?;
    }
    info!("Starting tasks consumption...");
    let (client2, _handle2) = await!(amqp_utils::connect_to_broker())?;
    let chan2 = await!(client2.create_channel())?;
    loop {
        let res = await!(chan2.basic_get(background_task_constants::TASKS_QUEUE, BasicGetOptions::default()))?;
        info!("Got result: {:?}", res);
        let msg = res.delivery;
        let task: BackgroundTask = serde_json::from_slice(&msg.data)?;
        task.execute()?;
        await!(channel.basic_ack(msg.delivery_tag, false))?;
        if let Some((hour, minute, second)) = task.get_next_schedule_time() {
let ttl = datetime_utils::compute_ttl_for_time(hour, minute, second);
        await!(background_task_delivery::perform_delivery_on(&channel, task, Some(ttl), false))?;
    }            
    }
    handle.stop();
    await!(channel.close(0, "Normal shutdown"))?;
    Ok(())
}

async fn consume_tasks() {
    if let Err(e) = await!(consume_tasks_real()) {
        error!("Error during task consumption: {}", e);
    }
}

fn main() -> Result<()> {
    server::init_logging();
    let _dotenv_path = dotenv::dotenv()?;
    tokio::run_async(consume_tasks());
    Ok(())
}
