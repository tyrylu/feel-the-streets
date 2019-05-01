use rusqlite::Row;
use rusqlite::MappedRows;
use rusqlite::Connection;
use rusqlite::CachedStatement;
use rusqlite::Result;
use rusqlite::types::{ToSql, FromSql};

pub struct SqliteMap<'a> {
    replace_key_value: CachedStatement<'a>,
    select_value: CachedStatement<'a>,
    select_key: CachedStatement<'a>,
    select_keys: CachedStatement<'a>,
    select_values: CachedStatement<'a>,
    select_keys_values: CachedStatement<'a>,
    delete_key: CachedStatement<'a>,
    select_count: CachedStatement<'a>,
    select_one: CachedStatement<'a>,
}

impl<'a> SqliteMap<'a> {
    pub fn new(connection: &'a Connection, tablename: &str, keytype: &str, valuetype: &str, is_first: bool) -> Result<Self> {
        if is_first {
        connection.execute(&format!("
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                key {} UNIQUE NOT NULL,
                value {} NOT NULL
            )", tablename, keytype, valuetype), &[])?;
        }
        let replace_key_value = connection.prepare_cached(&format!("INSERT OR REPLACE INTO {} (key, value) VALUES (?, ?)", tablename))?;
        let select_value = connection.prepare_cached(&format!("SELECT value FROM {} WHERE key=?", tablename))?;
        let select_key = connection.prepare_cached(&format!("SELECT 1 FROM {} WHERE key=?", tablename))?;
        let select_keys = connection.prepare_cached(&format!("SELECT key FROM {}", tablename))?;
        let select_values = connection.prepare_cached(&format!("SELECT value FROM {}", tablename))?;
        let select_keys_values = connection.prepare_cached(&format!("SELECT key, value FROM {}", tablename))?;
        let delete_key = connection.prepare_cached(&format!("DELETE FROM {} WHERE key=?", tablename))?;
        let select_count = connection.prepare_cached(&format!("SELECT COUNT(*) FROM {}", tablename))?;
        let select_one = connection.prepare_cached(&format!("SELECT 1 FROM {}", tablename))?;

        Ok(Self {
            replace_key_value,
            select_value,
            select_key,
            select_keys,
            select_values,
            select_keys_values,
            delete_key,
            select_count,
            select_one,
        })
    }

    pub fn insert<R>(&mut self, key: &ToSql, value: &ToSql) -> Result<Option<R>>
        where R: FromSql {

        let mut rows = self.select_value.query(&[key])?;
        let output = match rows.next() {
            Some(row) => row?.get_checked(0)?,
            None => None,
        };
        self.replace_key_value.execute(&[key, value])?;
        Ok(output)
    }

    pub fn get<R>(&mut self, key: &ToSql) -> Result<Option<R>>
        where R: FromSql {

        let mut rows = self.select_value.query(&[key])?;
        let row = match rows.next() {
            Some(row) => row?,
            None => return Ok(None),
        };
        Ok(Some(row.get_checked(0)?))
    }

    pub fn keys<R>(&mut self) -> Result<MappedRows<impl FnMut(&Row) -> R>>
        where R: FromSql {

        self.select_keys.query_map(&[], |row| row.get(0))
    }

    pub fn values<R>(&mut self) -> Result<MappedRows<impl FnMut(&Row) -> R>>
        where R: FromSql {

        self.select_values.query_map(&[], |row| row.get(0))
    }

    pub fn iter<K, V>(&mut self) -> Result<MappedRows<impl FnMut(&Row) -> (K, V)>>
        where K: FromSql,
              V: FromSql {

        self.select_keys_values.query_map(&[], |row| (row.get(0), row.get(1)))
    }

    pub fn contains_key(&mut self, key: &ToSql) -> Result<bool> {
        let mut rows = self.select_key.query(&[key])?;
        Ok(match rows.next() {
            Some(Ok(_)) => true,
            Some(Err(x)) => return Err(x),
            None => false,
        })
    }

    pub fn len(&mut self) -> Result<usize> {
        let mut rows = self.select_count.query(&[])?;
        let row = match rows.next() {
            Some(row) => row?,
            None => return Ok(0),
        };
        let size: isize = row.get_checked(0)?;
        Ok(size as usize)
    }

    pub fn remove<R>(&mut self, key: &ToSql) -> Result<Option<R>>
        where R: FromSql {

        let mut rows = self.select_value.query(&[key])?;
        let row = match rows.next() {
            Some(row) => row?,
            None => return Ok(None),
        };
        match row.get_checked(0) {
            Ok(value) => {
                self.delete_key.execute(&[key])?;
                Ok(Some(value))
            },
            Err(x) => Err(x)
        }
    }

    pub fn is_empty(&mut self) -> Result<bool> {
        let mut rows = self.select_one.query(&[])?;
        Ok(match rows.next() {
            Some(Ok(_)) => false,
            Some(Err(x)) => return Err(x),
            None => true,
        })
    }
}
