use crate::entities_query_condition::FieldCondition;
use rusqlite::types::ToSql;
use std::f64;

const RECTANGLE_CONDITION_SQL: &str = "(entities.rowid = idx_entities_geometry.pkid) AND (idx_entities_geometry.xmin <= :max_x) AND (idx_entities_geometry.xmax >= :min_x) AND (idx_entities_geometry.ymin <= :max_y) AND (idx_entities_geometry.ymax >= :min_y)";
const PARENT_ID_FILTER_SQL: &str = "id in (select child_id from entity_relationships where parent_id = :child_id";
const CHILD_ID_FILTER_SQL: &str = "id in (select parent_id from entity_relationships where child_id = :child_id";

pub struct EntitiesQuery {
    included_discriminators: Vec<String>,
    excluded_discriminators: Vec<String>,
    min_x: f64,
    max_x: f64,
    min_y: f64,
    max_y: f64,
    parent_id: Option<String>,
    child_id: Option<String>,
    conditions: Vec<FieldCondition>,
    limit: Option<usize>,
}

impl Default for EntitiesQuery {
    fn default() -> Self {
        EntitiesQuery {
            included_discriminators: Vec::new(),
            excluded_discriminators: Vec::new(),
            min_x: f64::NEG_INFINITY,
            max_x: f64::INFINITY,
            min_y: f64::NEG_INFINITY,
            max_y: f64::INFINITY,
            child_id: None,
            parent_id: None,
            conditions: Vec::new(),
            limit: None,
        }
    }
}
impl EntitiesQuery {
    pub fn set_included_discriminators(&mut self, discriminators: Vec<String>) {
        self.included_discriminators = discriminators;
    }

    pub fn set_excluded_discriminators(&mut self, discriminators: Vec<String>) {
        self.excluded_discriminators = discriminators;
    }

    pub fn set_rectangle_of_interest(&mut self, min_x: f64, max_x: f64, min_y: f64, max_y: f64) {
        self.min_x = min_x;
        self.max_x = max_x;
        self.min_y = min_y;
        self.max_y = max_y;
    }

    pub fn set_child_id(&mut self, id: String) {
        self.child_id = Some(id);
    }

    pub fn set_parent_id(&mut self, id: String) {
        self.parent_id = Some(id);
    }

    pub fn add_condition(&mut self, condition: FieldCondition) {
        self.conditions.push(condition);
    }

    pub fn set_limit(&mut self, limit: usize) {
        self.limit = Some(limit);
    }

    pub fn to_query_sql(&self) -> String {
        let base_query = "select id, discriminator, AsBinary(geometry) as geometry, data, effective_width from entities, idx_entities_geometry";
        let mut condition_fragments = vec![RECTANGLE_CONDITION_SQL.to_string()];
        let mut discriminator_placeholders = vec![];
        for idx in 0..self.included_discriminators.len() {
            discriminator_placeholders.push(format!(":included_discriminator{}", idx));
        }
        if !discriminator_placeholders.is_empty() {
            condition_fragments.push(format!(
                "discriminator IN ({})",
                discriminator_placeholders.join(",")
            ));
        }
        discriminator_placeholders.clear();
        for idx in 0..self.excluded_discriminators.len() {
            discriminator_placeholders.push(format!(":excluded_discriminator{}", idx));
        }
        if !discriminator_placeholders.is_empty() {
            condition_fragments.push(format!(
                "discriminator NOT IN ({})",
                discriminator_placeholders.join(",")
            ));
        }
        if self.child_id.is_some() {
            condition_fragments.push(CHILD_ID_FILTER_SQL.to_string());
        }
        if self.parent_id.is_some() {
            condition_fragments.push(PARENT_ID_FILTER_SQL.to_string());
        }
        for (idx, condition) in self.conditions.iter().enumerate() {
            condition_fragments.push(condition.to_query_fragment(idx));
        }
        if let Some(limit) = self.limit {
            format!(
                "{} WHERE {} LIMIT {}",
                base_query,
                condition_fragments.join(" AND "),
                limit
            )
        } else {
            format!("{} WHERE {}", base_query, condition_fragments.join(" AND "))
        }
    }

    pub fn to_query_params(&self) -> Vec<(String, &dyn ToSql)> {
        let mut params: Vec<(String, &dyn ToSql)> = vec![
            (":min_x".to_string(), &self.min_x),
            (":max_x".to_string(), &self.max_x),
            (":min_y".to_string(), &self.min_y),
            (":max_y".to_string(), &self.max_y),
        ];
        for (idx, discriminator) in self.included_discriminators.iter().enumerate() {
            params.push((format!(":included_discriminator{}", idx), discriminator));
        }
        for (idx, discriminator) in self.excluded_discriminators.iter().enumerate() {
            params.push((format!(":excluded_discriminator{}", idx), discriminator));
        }
        if self.child_id.is_some() {
            params.push((":child_id".to_string(), self.child_id.as_ref().unwrap()));
        }
        if self.parent_id.is_some() {
            params.push((":parent_id".to_string(), self.parent_id.as_ref().unwrap()));
        }
        
        for (idx, condition) in self.conditions.iter().enumerate() {

            if let Some(val) = condition.to_param_value() {
                params.push((format!(":param{}", idx), val));
            }
        }
        params
    }
}
