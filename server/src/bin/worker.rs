use lapin::options::{BasicAckOptions, BasicConsumeOptions, BasicQosOptions};
use lapin::types::FieldTable;
use log::{info, trace};
use server::{
    amqp_utils, background_task::BackgroundTask, background_task_constants,
    background_task_delivery, datetime_utils, Result,
};


fn consume_tasks() -> Result<()> {
    use background_task_constants::*;
    let client = amqp_utils::connect_to_broker()?;
    let mut channel = client.create_channel().wait()?;
    let channel2 = client.create_channel().wait()?;
    let (tasks_queue, future_tasks_queue) = amqp_utils::init_background_job_queues(&mut channel)?;
    let count = future_tasks_queue.message_count();
    if count == 0 {
        info!("Initially scheduling the databases update task...");
        let ttl = datetime_utils::compute_ttl_for_time(
            DATABASES_UPDATE_HOUR,
            DATABASES_UPDATE_MINUTE,
            DATABASES_UPDATE_SECOND,
        );
        background_task_delivery::perform_delivery_on(
            &channel2,
            &BackgroundTask::UpdateAreaDatabases,
            Some(ttl),
        )?;
    }
    let opts = BasicQosOptions {
        ..Default::default()
    };
    channel.basic_qos(1, opts).wait()?;
    let consumer = channel
                .basic_consume(
            &tasks_queue.name().as_str(),
            "tasks_consumer",
            BasicConsumeOptions::default(),
            FieldTable::default(),
        )
        .wait()?;
    info!("Starting tasks consumption...");
    for delivery in consumer {
        let delivery_obj = delivery?;
        trace!("Received message: {:?}", delivery_obj);
        let task: BackgroundTask = serde_json::from_slice(&delivery_obj.data)?;
        task.execute()?;
        info!("Task executed successfully.");
        channel
            .basic_ack(delivery_obj.delivery_tag, BasicAckOptions::default())
            .wait()?;
        info!("Task acknowledged.");
        if let Some((hour, minute, second)) = task.get_next_schedule_time() {
            let ttl = datetime_utils::compute_ttl_for_time(hour, minute, second);
            background_task_delivery::perform_delivery_on(&channel2 , &task, Some(ttl))?;
        }
        
    }
    client.run()?;
    Ok(())
}

fn main() -> Result<()> {
    server::init_logging();
    let _dotenv_path = dotenv::dotenv()?;
    consume_tasks()
}
