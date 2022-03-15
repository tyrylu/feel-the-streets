use crate::Result;
use chrono::{DateTime, Duration, Utc};
use log::{debug, warn};
use once_cell::sync::Lazy;
use regex::Regex;
use std::cell::RefCell;
use std::io::{self, Read, Seek, SeekFrom};
use std::time::Instant;
use tempfile::tempfile;

const QUERY_RETRY_COUNT: u8 = 3;

static AVAILABLE_SLOTS_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^(\d+) slots available now.").unwrap());
static SLOT_AVAILABLE_AFTER_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^Slot available after: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)").unwrap()
});
static RATE_LIMIT_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^Rate limit: (\d+)").unwrap());

fn getting_non_200_response_is_ok(
    err: ureq::Error,
) -> std::result::Result<ureq::Response, ureq::Error> {
    match err {
        ureq::Error::Status(_, resp) => Ok(resp),
        _ => Err(err),
    }
}

pub struct OverpassApiServer {
    http_client: ureq::Agent,
    url: &'static str,
    available_slots: RefCell<usize>,
    slots_available_after: RefCell<Vec<DateTime<Utc>>>,
    rate_limit: RefCell<usize>,
}

impl OverpassApiServer {
    pub fn new(url: &'static str) -> Result<Self> {
        let ret = Self {
            http_client: ureq::Agent::new(),
            available_slots: RefCell::new(0),
            slots_available_after: RefCell::new(vec![]),
            rate_limit: RefCell::new(0),
            url,
        };
        ret.update_status()?;
        Ok(ret)
    }

    pub fn run_query(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read>> {
        let mut res = None;
        for retry in 0..QUERY_RETRY_COUNT {
            res = match self.run_query_internal(query, result_to_tempfile) {
                Ok(r) => Some(Ok(r)),
                Err(e) => {
                    warn!("Query failed during retry {}, error: {:?}, we had {:?} available slots with available times {:?}.", retry, e, self.available_slots, self.slots_available_after);
                    Some(Err(e))
                }
            };
            match res {
                Some(Ok(_)) => break,
                Some(Err(_)) => {}
                None => panic!("What? That should not have happened..."),
            }
        }
        res.unwrap()
    }

    fn run_query_internal(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read>> {
        let start = Instant::now();
        let final_url = format!("{}/api/interpreter", self.url);
        debug!("Requesting resource {}", final_url);
        let resp = self
            .http_client
            .post(&final_url)
            .send_form(&[("data", query)])
            .or_else(getting_non_200_response_is_ok)?;
        self.update_status()?;
        match resp.status() {
            200 => {
                debug!("Request successfully finished after {:?}.", start.elapsed());
                if !result_to_tempfile {
                    Ok(Box::new(resp.into_reader()))
                } else {
                    let mut file = tempfile()?;
                    io::copy(&mut resp.into_reader(), &mut file)?;
                    file.seek(SeekFrom::Start(0))?;
                    Ok(Box::new(file))
                }
            }
            _ => {
                warn!("Unexpected status code {} from the server. We now have {:?} slots with availability times {:?}.", resp.status(), self.available_slots, self.slots_available_after);
                self.run_query(query, result_to_tempfile)
            }
        }
    }

    fn update_status(&self) -> Result<()> {
        *self.available_slots.borrow_mut() = 0;
        self.slots_available_after.borrow_mut().clear();
        let text = self
            .http_client
            .get(&format!("{}/api/status", self.url))
            .call()?
            .into_string()?;
        for line in text.lines() {
            let rate_limit_match = RATE_LIMIT_RE.captures(line);
            if let Some(res) = rate_limit_match {
                *self.rate_limit.borrow_mut() = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_count_match = AVAILABLE_SLOTS_RE.captures(line);
            if let Some(res) = available_count_match {
                *self.available_slots.borrow_mut() = res.get(1).unwrap().as_str().parse().unwrap();
            }
            let available_after_match = SLOT_AVAILABLE_AFTER_RE.captures(line);
            if let Some(res) = available_after_match {
                let date_str = res.get(1).unwrap().as_str();
                self.slots_available_after.borrow_mut().push(
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
        *self.rate_limit.borrow() == 0 ||
        *self.available_slots.borrow() > 0
            || self.slots_available_after.borrow().iter().any(|s| s < &now)
    }

    pub fn slot_available_after(&self) -> Duration {
        if *self.available_slots.borrow() > 0 || *self.rate_limit.borrow() == 0 {
            Duration::zero()
        } else {
            *self.slots_available_after.borrow().iter().min().unwrap() - Utc::now()
        }
    }
}
