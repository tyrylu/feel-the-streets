use super::server;
use crate::{Error, Result};
use crossbeam_channel::Sender;
use log::warn;
use rand::seq::SliceRandom;
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
    command_senders: Vec<Sender<ServerQuery>>,
    should_exit: Arc<AtomicBool>,
}

impl Default for Servers {
    fn default() -> Self {
        Self::with_server_urls(vec![
            "https://overpass-api.de",
            //"https://overpass.private.coffee",
            //"https://maps.mail.ru/osm/tools/overpass",
        ])
    }
}

impl Servers {
    pub fn with_server_urls(urls: Vec<&'static str>) -> Self {
        let mut senders = Vec::with_capacity(urls.len());
        let should_exit = Arc::new(AtomicBool::new(false));
        for url in urls {
            let (tx, rx) = crossbeam_channel::unbounded();
            let rx_clone = rx.clone();
            let exit_clone = should_exit.clone();
            senders.push(tx);
            thread::spawn(move || server::requests_dispatcher(url, rx_clone, exit_clone));
        }
        Self {
            command_senders: senders,
            should_exit,
        }
    }

    pub fn run_query(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read + Send>> {
        for retry in 0..100 {
            let mut servers_order: Vec<usize> = (0..self.command_senders.len()).collect();
            let mut rng = rand::rng();
            servers_order.shuffle(&mut rng);
            for i in servers_order {
            let (tx, rx) = crossbeam_channel::bounded(1);
            self.command_senders[i]
                .send(ServerQuery {
                    query: query.to_string(),
                    result_sender: tx,
                    result_to_tempfile,
                })
                .unwrap();
            match rx.recv().unwrap() {
                Ok(ret) => return Ok(ret),
                Err(Error::RetryLimitExceeded) => {
                    warn!("Query failed to be processed by overpass API server with index {}, trying the next.", i);
                    continue;
                }
                Err(e) => return Err(e),
            }
        }
        warn!(
            "Query failed to be processed by all overpass API servers, retrying (attempt {}/{})",
            retry + 1,
            100
        );
    }
            Err(Error::RetryLimitExceeded)
    }
}

impl Drop for Servers {
    fn drop(&mut self) {
        self.should_exit.store(true, Ordering::SeqCst);
    }
}
