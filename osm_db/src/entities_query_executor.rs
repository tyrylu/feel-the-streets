use crate::area_db::AreaDatabase;
use crate::entities_query::EntitiesQuery;
use rusqlite::{CachedStatement, Rows};
use std::time::Instant;

pub struct EntitiesQueryExecutor<'a> {
    query: &'a EntitiesQuery,
    statement: Option<CachedStatement<'a>>,
}
impl<'a> EntitiesQueryExecutor<'a> {
    pub fn new(query: &'a EntitiesQuery) -> Self {
        EntitiesQueryExecutor {
            query,
            statement: None,
        }
    }

    pub fn prepare_execute(&mut self, conn: &'a AreaDatabase) -> rusqlite::Result<Rows> {
        debug!("About to execute query {}", self.query.to_query_sql());
        self.statement = Some(conn.conn.prepare_cached(&self.query.to_query_sql())?);
        let orig_params = self.query.to_query_params();
        let mut params = vec![];
        for (name, value) in &orig_params {
            params.push((name.as_str(), *value));
        }
        let now = Instant::now();
        let res = self
            .statement
            .as_deref_mut()
            .unwrap()
            .query_named(params.as_slice())?;
        debug!("Query_named took {:?}", now.elapsed());
        Ok(res)
    }
}
