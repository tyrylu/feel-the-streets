use std::{io::Read, sync::{atomic::{AtomicBool, Ordering}, Arc}};
use crate::Result;
use super::server;
use crossbeam_channel::Sender;
use std::thread;

pub struct ServerQuery { pub query: String, pub result_to_tempfile: bool, pub result_sender:  Sender<Result<Box<dyn Read + Send>>>}

pub struct Servers {
    commands_sender: Sender<ServerQuery>,
    should_exit: Arc<AtomicBool>
}

impl Default for Servers {
    fn default() -> Self {
        Self::with_server_urls(vec![
            "https://z.overpass-api.de",
            "https://lz4.overpass-api.de",
            "https://overpass.kumi.systems",
            "https://maps.mail.ru/osm/tools/overpass"
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
        Self { commands_sender: tx, should_exit }
    }

    pub fn run_query(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read + Send>> {
        let (tx, rx) = crossbeam_channel::bounded(1);
        self.commands_sender.send(ServerQuery { query: query.to_string(), result_sender: tx, result_to_tempfile }).unwrap();
        rx.recv().unwrap()
    }
}

impl Drop for Servers {
    fn drop(&mut self) {
        self.should_exit.store(true, Ordering::SeqCst);
    }
}