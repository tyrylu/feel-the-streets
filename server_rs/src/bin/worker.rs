#![feature(await_macro, async_await, futures_api)]
extern crate server_rs;
use server_rs::{amqp_utils, background_task::BackgroundTask, background_task_constants, Result};
use tokio::await;
use tokio::prelude::*;

use lapin_futures::channel::BasicConsumeOptions;
use lapin_futures::queue::Queue;
use lapin_futures::types::FieldTable;
use log::error;

async fn consume_tasks_real() -> Result<()> {
    let client = await!(amqp_utils::connect_to_broker())?;
    await!(amqp_utils::init_background_job_queues(&client))?;
    let channel = await!(client.create_channel())?;
    let queue = Queue::new(background_task_constants::TASKS_QUEUE.to_string(), 0, 0);
    let mut consumer = await!(channel.basic_consume(
        &queue,
        "tasks_consumer",
        BasicConsumeOptions::default(),
        FieldTable::new()
    ))?;
    while let Some(msg) = await!(consumer.next()) {
        let msg = msg?;
        let task: BackgroundTask = serde_json::from_slice(&msg.data)?;
        task.execute()?;
    }
    Ok(())
}

async fn consume_tasks() {
    if let Err(e) = await!(consume_tasks_real()) {
        error!("Error during task consumption: {}", e);
    }
}

fn main() -> Result<()> {
    env_logger::init();
    let _dotenv_path = dotenv::dotenv()?;
    tokio::run_async(consume_tasks());
    Ok(())
}
