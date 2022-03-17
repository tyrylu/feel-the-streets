use chrono::{DateTime, Utc, Duration};
use crossbeam_channel::{Sender, Receiver};
use log::{warn, debug, info};
use once_cell::sync::Lazy;
use regex::Regex;
use super::servers::ServerQuery;
use ureq::{Agent, Request};
use crate::{Result, Error};
use std::sync::Arc;
use std::thread;
use std::sync::atomic::{AtomicBool, Ordering};
use std::io::{self, Read, Seek, SeekFrom};
use tempfile::tempfile;
use std::time::Instant;

static AVAILABLE_SLOTS_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^(\d+) slots available now.").unwrap());
static SLOT_AVAILABLE_AFTER_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^Slot available after: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)").unwrap()
});
static RATE_LIMIT_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^Rate limit: (\d+)").unwrap());

    const QUERY_RETRY_COUNT: u8 = 6;

fn query_executor(req: Request, query: ServerQuery, wake_sender: Sender<()>) {
    let mut retry = 0;
    let ret = loop {
        retry += 1;
        if retry > QUERY_RETRY_COUNT {
            break Err(Error::RetryLimitExceeded)
        }
        match run_query(req.clone(), &query.query, query.result_to_tempfile, &wake_sender) {
            Ok(r) => break Ok(r),
            Err(e) => {
                warn!("Query failed during retry {}, error: {:?}.", retry, e);
            }
        }
    };
    query.result_sender.send(ret).unwrap();
}

fn run_query(req: Request, query: &str, result_to_tempfile: bool, wake_sender: &Sender<()>) -> Result<Box<dyn Read + Send>> {
    let start = Instant::now();
    debug!("Calling interpreter endpoint {} with query {}", req.url(), query);
    let resp = req
        .send_form(&[("data", query)])?;
    debug!("Request successfully finished after {:?}.", start.elapsed());
    // Maybe wake the dispatcher
    wake_sender.send(()).unwrap();
    if !result_to_tempfile {
        Ok(Box::new(resp.into_reader()))
    } else {
        let mut file = tempfile()?;
        io::copy(&mut resp.into_reader(), &mut file)?;
        file.seek(SeekFrom::Start(0))?;
        Ok(Box::new(file))
    }
}

pub fn requests_dispatcher(url: &'static str, queries_receiver: Receiver<ServerQuery>, should_exit: Arc<AtomicBool>) {
    let mut server = Server::new(url).expect("Could not create server");
    let mut in_flight_requests = 0;
    let (wake_tx, wake_rx) = crossbeam_channel::unbounded();
    while !should_exit.load(Ordering::SeqCst) {
        // In the previous iteration, we finished at least one in-flight query, and we have the current quota status, so how much must we sleep to make a query slot available to us?
        if !server.has_available_slot() {
            let dur = server.slot_available_after().to_std().unwrap();
            info!("Overpass API endpoint at {} ran out of slots, going to sleep for {:?} to make one.", url, dur);
            thread::sleep(dur);
        }
        // Now, we have at least one slot available, so get something to work on.
        if let Ok(query) = queries_receiver.recv() {
            let req = server.prepare_run_query();
            in_flight_requests += 1;
            let wake_clone = wake_tx.clone();
            thread::spawn(move || query_executor(req, query, wake_clone));
            // Did we reach the maximum nuber of in-flight queries? If yes, wait for at leas one to finish.
            if server.rate_limit > 0 && server.rate_limit == in_flight_requests {
                let _ = wake_rx.recv().unwrap();
                in_flight_requests -= 1;
                // The wake could have been from a request which finished while we slept and others could finish as well, so find out how many actually did.
                while let Ok(()) = wake_rx.try_recv() {
                    in_flight_requests -= 1;
                }
            }
            server.update_status().expect("Could not update status");
        }
        else {
            // The Servers instance got dropped, so just exit gracefully.
            break;
        }
    }
}

struct Server {
    url: &'static str,
    agent: Agent,
    pub rate_limit: usize,
    available_slots: usize,
    slots_available_after: Vec<DateTime<Utc>>
}

impl Server {
    fn new(url: &'static str) -> Result<Self> {
        let mut this = Self { agent: Agent::new(), available_slots: 0, rate_limit: 0, slots_available_after: vec![], url };
        this.update_status()?;
        Ok(this)
    }
    fn update_status(&mut self) -> Result<()> {
        self.available_slots = 0;
        self.slots_available_after.clear();
        let text = self
            .agent
            .get(&format!("{}/api/status", self.url))
            .call()?
            .into_string()?;
        for line in text.lines() {
            let rate_limit_match = RATE_LIMIT_RE.captures(line);
            if let Some(res) = rate_limit_match {
                self.rate_limit = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_count_match = AVAILABLE_SLOTS_RE.captures(line);
            if let Some(res) = available_count_match {
                self.available_slots = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_after_match = SLOT_AVAILABLE_AFTER_RE.captures(line);
            if let Some(res) = available_after_match {
                let date_str = res.get(1).unwrap().as_str();
                self.slots_available_after.push(
                    DateTime::parse_from_rfc3339(date_str)
                        .unwrap()
                        .with_timezone(&Utc),
                );
            }
        }
        Ok(())
    }

    pub fn has_available_slot(&self) -> bool {
        let now = Utc::now();
        self.rate_limit == 0 ||
        self.available_slots > 0
            || self.slots_available_after.iter().any(|s| s < &now)
    }

    pub fn slot_available_after(&self) -> Duration {
         if self.available_slots > 0 || self.rate_limit == 0 {
            Duration::zero()
        } else {
            *self.slots_available_after.iter().min().unwrap() - Utc::now()
        }
    }

    pub fn prepare_run_query(&self) -> Request {
        let final_url = format!("{}/api/interpreter", self.url);
        self.agent
            .post(&final_url)
    }
}