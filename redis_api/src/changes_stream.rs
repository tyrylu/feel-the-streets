use crate::changes_batch::ChangesBatch;
use crate::Result;
use osm_db::semantic_change::SemanticChange;
use redis::acl::Rule;
use redis::streams::{StreamInfoGroupsReply, StreamMaxlen};
use redis::{Client, Commands, Connection};
use std::collections::HashMap;
use std::env;

#[allow(clippy::len_without_is_empty)]
pub struct ChangesStream {
    area_id: i64,
    redis_connection: Connection,
}

impl ChangesStream {
    pub fn new(area_id: i64, redis_connection_string: &str) -> Result<Self> {
        let conn = Client::open(redis_connection_string)?.get_connection()?;
        Ok(Self {
            area_id,
            redis_connection: conn,
        })
    }

    pub fn new_from_env(area_id: i64) -> Result<Self> {
        Self::new(
            area_id,
            &env::var("REDIS_URL").expect("REDIS_URL missing in the environment"),
        )
    }

    fn changes_key(&self) -> String {
        format!("fts.{}.changes", self.area_id)
    }

    fn redownload_requests_key(&self) -> String {
        format!("fts.{}.redownload_requests", self.area_id)
    }

    fn change_counts_key(&self) -> String {
        format!("fts.{}.change_counts", self.area_id)
    }

    pub(crate) fn add_change(&mut self, change: &SemanticChange) -> Result<()> {
        self.redis_connection
            .xadd(self.changes_key(), "*", &[("c", change.serialize()?)])?;
        Ok(())
    }

    pub fn register_client(&mut self, client_id: &str) -> Result<()> {
        self.redis_connection
            .xgroup_create_mkstream(self.changes_key(), client_id, "$")?;
        self.redis_connection.acl_setuser_rules(
            client_id,
            &[Rule::Pattern(format!("fts.{}.*", self.area_id))],
        )?;
        self.redis_connection.acl_save()?;
        Ok(())
    }

    pub fn create_client(&mut self, client_id: &str) -> Result<String> {
        let password: String = self.redis_connection.acl_genpass()?;
        self.redis_connection.acl_setuser_rules(
            client_id,
            &[
                Rule::On,
                Rule::AddPass(password.clone()),
                Rule::AddCommand("ping".to_string()),
                Rule::AddCommand("xreadgroup".to_string()),
                Rule::AddCommand("xack".to_string()),
                Rule::AddCommand("sismember".to_string()),
                Rule::AddCommand("hget".to_string()),
                Rule::AddCommand("hincrby".to_string()),
                Rule::AddCommand("exists".to_string()),
            ],
        )?;
        self.redis_connection.acl_save()?;
        Ok(password)
    }

    pub fn is_redownload_requested_for(&mut self, client_id: &str) -> Result<bool> {
        let res: bool = self
            .redis_connection
            .sismember(self.redownload_requests_key(), client_id)?;
        Ok(res)
    }

    pub fn request_redownload_for(&mut self, client_ids: &[&str]) -> Result<()> {
        let zero_pairs: Vec<(&str, u64)> = client_ids.iter().map(|i| (*i, 0)).collect();
        redis::pipe()
            .atomic()
            .sadd(self.redownload_requests_key(), client_ids)
            .ignore()
            .hset_multiple(self.change_counts_key(), &zero_pairs)
            .query(&mut self.redis_connection)?;

        Ok(())
    }

    pub fn redownload_finished_for(&mut self, client_id: &str) -> Result<()> {
        redis::pipe()
            .atomic()
            .srem(self.redownload_requests_key(), client_id)
            .ignore()
            .xgroup_setid(self.changes_key(), client_id, "$")
            .ignore()
            .query(&mut self.redis_connection)?;

        Ok(())
    }

    pub fn registered_clients(&mut self) -> Result<Vec<String>> {
        if !self.exists()? {
            Ok(vec![])
        } else {
            let reply: StreamInfoGroupsReply =
                self.redis_connection.xinfo_groups(self.changes_key())?;
            Ok(reply.groups.iter().map(|g| g.name.clone()).collect())
        }
    }

    pub fn request_redownload(&mut self) -> Result<()> {
        let client_ids = self.registered_clients()?;
        if client_ids.is_empty() {
            // This stream has no clients, so we have to notify nobody about the redownload request.
            Ok(())
        } else {
            let client_id_refs: Vec<&str> = client_ids.iter().map(|s| s.as_ref()).collect();
            self.request_redownload_for(&client_id_refs)?;
            Ok(())
        }
    }

    pub fn should_publish_changes(&mut self) -> Result<bool> {
        let mut registered = self.registered_clients()?;
        let mut should_redownload: Vec<String> = self
            .redis_connection
            .smembers(self.redownload_requests_key())?;
        registered.sort();
        should_redownload.sort();
        Ok(registered != should_redownload)
    }

    pub fn has_client(&mut self, client_id: &str) -> Result<bool> {
        if !self.exists()? {
            Ok(false)
        } else {
            let reply: StreamInfoGroupsReply =
                self.redis_connection.xinfo_groups(self.changes_key())?;
            Ok(reply.groups.iter().any(|g| g.name == client_id))
        }
    }

    pub fn exists(&mut self) -> Result<bool> {
        let res: bool = self.redis_connection.exists(self.changes_key())?;
        Ok(res)
    }

    pub fn garbage_collect(&mut self) -> Result<u64> {
        if !self.exists()? {
            Ok(0)
        } else {
            let reply: StreamInfoGroupsReply =
                self.redis_connection.xinfo_groups(self.changes_key())?;
            let mut last_ids: Vec<&str> = reply
                .groups
                .iter()
                .map(|g| g.last_delivered_id.as_ref())
                .collect();
            last_ids.sort_unstable();
            let first_id = last_ids
                .first()
                .expect("We should always have at least one id");
            // The high level xtrim abstraction does not support specifiing the MINID argument, so we have to call this one manually.
            let num: u64 = redis::cmd("xtrim")
                .arg(self.changes_key())
                .arg("MINID")
                .arg(*first_id)
                .query(&mut self.redis_connection)?;
            Ok(num)
        }
    }

    pub fn memory_usage(&mut self) -> Result<u64> {
        if self.exists()? {
            Ok(redis::cmd("memory")
                .arg("usage")
                .arg(self.changes_key())
                .query(&mut self.redis_connection)?)
        } else {
            Ok(0)
        }
    }

    pub fn trim_to_exact_length(&mut self, length: usize) -> Result<usize> {
        let removed: usize = self
            .redis_connection
            .xtrim(self.changes_key(), StreamMaxlen::Equals(length))?;
        Ok(removed)
    }

    pub fn begin_batch(&mut self) -> ChangesBatch {
        ChangesBatch::for_stream(self)
    }

    pub(crate) fn increment_changes_count_by(&mut self, count: u64) -> Result<()> {
        let mut pipe = redis::pipe();
        let mut pipe_ref = pipe.atomic();
        for client_id in self.registered_clients()? {
            if !(self.is_redownload_requested_for(&client_id)?) {
                pipe_ref = pipe_ref
                    .hincr(self.change_counts_key(), client_id, count)
                    .ignore();
            }
        }
        pipe.query(&mut self.redis_connection)?;
        Ok(())
    }

    pub fn len(&mut self) -> Result<usize> {
        if self.exists()? {
            Ok(self.redis_connection.xlen(self.changes_key())?)
        } else {
            Ok(0)
        }
    }

    pub fn connect_to_stream(&mut self, area_id: i64) {
        self.area_id = area_id;
    }

    pub fn all_change_counts(&mut self) -> Result<HashMap<String, u64>> {
        Ok(self.redis_connection.hgetall(self.change_counts_key())?)
    }

    pub fn all_redownload_requests(&mut self) -> Result<Vec<String>> {
        Ok(self
            .redis_connection
            .smembers(self.redownload_requests_key())?)
    }
}
