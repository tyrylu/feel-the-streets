use super::server;
use crate::{Error, Result};
use crossbeam_channel::Sender;
use log::warn;
use std::thread;
use std::{
    io::Read,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
};

pub struct ServerQuery {
    pub query: String,
    pub result_to_tempfile: bool,
    pub result_sender: Sender<Result<Box<dyn Read + Send>>>,
}

pub struct Servers {
    commands_sender: Sender<ServerQuery>,
    should_exit: Arc<AtomicBool>,
}

impl Default for Servers {
    fn default() -> Self {
        Self::with_server_urls(vec![
            "https://overpass-api.de",
            "https://overpass.private.coffee",
            "https://maps.mail.ru/osm/tools/overpass",
        ])
    }
}

impl Servers {
    pub fn with_server_urls(urls: Vec<&'static str>) -> Self {
        let (tx, rx) = crossbeam_channel::unbounded();
        let should_exit = Arc::new(AtomicBool::new(false));
        for url in urls {
            let rx_clone = rx.clone();
            let exit_clone = should_exit.clone();
            thread::spawn(move || server::requests_dispatcher(url, rx_clone, exit_clone));
        }
        Self {
            commands_sender: tx,
            should_exit,
        }
    }

    pub fn run_query(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read + Send>> {
        for retry in 0..100 {
            let (tx, rx) = crossbeam_channel::bounded(1);
            self.commands_sender
                .send(ServerQuery {
                    query: query.to_string(),
                    result_sender: tx,
                    result_to_tempfile,
                })
                .unwrap();
            match rx.recv().unwrap() {
                Ok(ret) => return Ok(ret),
                Err(Error::RetryLimitExceeded) => {
                    warn!("Query failed to be processed by an overpass API server, this is the {}. occurrence.", retry + 1);
                    continue;
                }
                Err(e) => return Err(e),
            }
        }
        Err(Error::RetryLimitExceeded)
    }
}

impl Drop for Servers {
    fn drop(&mut self) {
        self.should_exit.store(true, Ordering::SeqCst);
    }
}
