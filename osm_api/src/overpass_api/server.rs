use super::servers::ServerQuery;
use crate::{Error, Result};
use backon::{BlockingRetryable, ExponentialBuilder};
use chrono::{DateTime, Duration, Utc};
use crossbeam_channel::{Receiver, Sender};
use log::{debug, info, warn};
use once_cell::sync::Lazy;
use regex::Regex;
use std::io::{self, Read, Seek};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;
use tempfile::tempfile;
use ureq::{Agent, Request};

static AVAILABLE_SLOTS_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^(\d+) slots available now.").unwrap());
static SLOT_AVAILABLE_AFTER_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^Slot available after: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)").unwrap()
});
static RATE_LIMIT_RE: Lazy<Regex> = Lazy::new(|| Regex::new(r"^Rate limit: (\d+)").unwrap());

fn query_executor(server: Server, query: ServerQuery, wake_sender: Sender<()>) {
    let req = server.prepare_run_query();
    let try_run_query = || {
        run_query(
            req.clone(),
            &query.query,
            query.result_to_tempfile,
            &wake_sender,
        )
    };
    let ret = try_run_query
        .retry(&ExponentialBuilder::default())
        .notify(|e, dur| {
            warn!(
                "Query failed, error: {:?}, going to sleep for {:?}.",
                e, dur
            );
            server
                .get_api_status()
                .expect("Could not get status during a retry")
                .wait_for_available_slot();
        })
        .call()
        .map_err(|_| Error::RetryLimitExceeded);
    query.result_sender.send(ret).unwrap();
}

fn run_query(
    req: Request,
    query: &str,
    result_to_tempfile: bool,
    wake_sender: &Sender<()>,
) -> Result<Box<dyn Read + Send>> {
    let start = Instant::now();
    debug!(
        "Calling interpreter endpoint {} with query {}",
        req.url(),
        query
    );
    let resp = req.send_form(&[("data", query)])?;
    debug!("Request successfully finished after {:?}.", start.elapsed());
    // Maybe wake the dispatcher
    wake_sender.send(()).unwrap();
    if !result_to_tempfile {
        Ok(Box::new(resp.into_reader()))
    } else {
        let mut file = tempfile()?;
        io::copy(&mut resp.into_reader(), &mut file)?;
        file.rewind()?;
        Ok(Box::new(file))
    }
}

pub fn requests_dispatcher(
    url: &'static str,
    queries_receiver: Receiver<ServerQuery>,
    should_exit: Arc<AtomicBool>,
) {
    let server = Server::new(url);
    let mut in_flight_requests = 0;
    let (wake_tx, wake_rx) = crossbeam_channel::unbounded();
    while !should_exit.load(Ordering::SeqCst) {
        // Wait until we have at least one available slot
        let status = server.get_api_status().expect("Could not get status");
        status.wait_for_available_slot();
        // Now, we have at least one slot available, so get something to work on.
        if let Ok(query) = queries_receiver.recv() {
            in_flight_requests += 1;
            let wake_clone = wake_tx.clone();
            let server_clone = server.clone();
            thread::spawn(move || query_executor(server_clone, query, wake_clone));
            // Did we reach the maximum nuber of in-flight queries? If yes, wait for at leas one to finish.
            if status.rate_limit > 0 && status.rate_limit == in_flight_requests {
                wake_rx.recv().unwrap();
                in_flight_requests -= 1;
                // The wake could have been from a request which finished while we slept and others could finish as well, so find out how many actually did.
                while let Ok(()) = wake_rx.try_recv() {
                    in_flight_requests -= 1;
                }
            }
        } else {
            // The Servers instance got dropped, so just exit gracefully.
            break;
        }
    }
}

struct ServerStatus {
    rate_limit: usize,
    available_slots: usize,
    slots_available_after: Vec<DateTime<Utc>>,
    url: &'static str,
}

impl ServerStatus {
    fn empty(url: &'static str) -> Self {
        Self {
            rate_limit: 0,
            available_slots: 0,
            slots_available_after: vec![],
            url,
        }
    }

    fn has_available_slot(&self) -> bool {
        let now = Utc::now();
        self.rate_limit == 0
            || self.available_slots > 0
            || self.slots_available_after.iter().any(|s| s < &now)
    }

    fn slot_available_after(&self) -> Duration {
        if self.available_slots > 0 || self.rate_limit == 0 {
            Duration::zero()
        } else {
            match self.slots_available_after.iter().min() {
                Some(dt) => *dt - Utc::now(),
                None => Duration::seconds(5), // Handles the case when all slots are taken and we are requested to get the sleep value.
            }
        }
    }

    fn wait_for_available_slot(&self) {
        if !self.has_available_slot() {
            let dur = self.slot_available_after().to_std().unwrap();
            info!("Overpass API endpoint at {} ran out of slots, going to sleep for {:?} to make one.", self.url, dur);
            thread::sleep(dur);
        }
    }
}

#[derive(Clone)]
struct Server {
    url: &'static str,
    agent: Agent,
}

impl Server {
    fn new(url: &'static str) -> Self {
        Self {
            agent: Agent::new(),
            url,
        }
    }
    fn get_api_status_text(&self) -> Result<String> {
        Ok(self
            .agent
            .get(&format!("{}/api/status", self.url))
            .call()?
            .into_string()?)
    }

    fn get_api_status(&self) -> Result<ServerStatus> {
        let get_text = || self.get_api_status_text();
        let text = get_text.retry(&ExponentialBuilder::default())
        .notify(|e, dur| { warn!("Could not get status from Overpass API endpoint at {}, error: {:?}, going to sleep for {:?}.", self.url, e, dur); })
        .call()
        .map_err(|_| Error::RetryLimitExceeded)?;
        let mut status = ServerStatus::empty(self.url);
        for line in text.lines() {
            let rate_limit_match = RATE_LIMIT_RE.captures(line);
            if let Some(res) = rate_limit_match {
                status.rate_limit = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_count_match = AVAILABLE_SLOTS_RE.captures(line);
            if let Some(res) = available_count_match {
                status.available_slots = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_after_match = SLOT_AVAILABLE_AFTER_RE.captures(line);
            if let Some(res) = available_after_match {
                let date_str = res.get(1).unwrap().as_str();
                status.slots_available_after.push(
                    DateTime::parse_from_rfc3339(date_str)
                        .unwrap()
                        .with_timezone(&Utc),
                );
            }
        }
        Ok(status)
    }

    fn prepare_run_query(&self) -> Request {
        let final_url = format!("{}/api/interpreter", self.url);
        self.agent.post(&final_url)
    }
}
