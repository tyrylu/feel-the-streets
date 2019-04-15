use chrono::prelude::*;
use chrono::Duration;

pub fn next_occurrence_of_time(hour: u32, minute: u32, second: u32) -> DateTime<Utc> {
    let now = Utc::now();
    let today = Utc::today().and_hms(hour, minute, second);
    if today > now {
        today
    } else {
        (now.date() + Duration::days(1)).and_hms(hour, minute, second)
    }
}

pub fn compute_ttl_for_time(hour: u32, minute: u32, second: u32) -> u32 {
    let occurrence = next_occurrence_of_time(hour, minute, second);
    let diff = occurrence - Utc::now();
    diff.num_milliseconds() as u32
}
