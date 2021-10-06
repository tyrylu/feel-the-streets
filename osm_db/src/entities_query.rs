use crate::entities_query_condition::FieldCondition;
use crate::entity_relationship_kind::EntityRelationshipKind;
use rusqlite::types::ToSql;
use std::f64;

const RECTANGLE_CONDITION_SQL: &str = "(entities.rowid = idx_entities_geometry.pkid) AND (idx_entities_geometry.xmin <= :max_x) AND (idx_entities_geometry.xmax >= :min_x) AND (idx_entities_geometry.ymin <= :max_y) AND (idx_entities_geometry.ymax >= :min_y)";
const CHILD_ID_FILTER_SQL: &str =
    "id in (select child_id from entity_relationships where parent_id = :parent_id";
const PARENT_ID_FILTER_SQL: &str =
    "id in (select parent_id from entity_relationships where child_id = :child_id";

pub struct EntitiesQuery {
    included_discriminators: Vec<String>,
    excluded_discriminators: Vec<String>,
    min_x: f64,
    max_x: f64,
    min_y: f64,
    max_y: f64,
    has_interest_rectangle: bool,
    parent_id: Option<String>,
    child_id: Option<String>,
    relationship_kind: Option<EntityRelationshipKind>,
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
            has_interest_rectangle: false,
            child_id: None,
            parent_id: None,
            relationship_kind: None,
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
        self.has_interest_rectangle = true;
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

    pub fn set_relationship_kind(&mut self, kind: EntityRelationshipKind) {
        self.relationship_kind = Some(kind);
    }

    pub fn add_condition(&mut self, condition: FieldCondition) {
        self.conditions.push(condition);
    }

    pub fn set_limit(&mut self, limit: usize) {
        self.limit = Some(limit);
    }

    pub fn to_query_sql(&self) -> String {
        let base_query = if self.has_interest_rectangle {
            "select id, discriminator, AsBinary(geometry) as geometry, data, effective_width from entities, idx_entities_geometry"
        } else {
            "select id, discriminator, AsBinary(geometry) as geometry, data, effective_width from entities"
        };
        let mut condition_fragments = if self.has_interest_rectangle {
            vec![RECTANGLE_CONDITION_SQL.to_string()]
        } else {
            Vec::new()
        };
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
            condition_fragments.push(self.prepare_relationship_id_filter(CHILD_ID_FILTER_SQL));
        }
        if self.parent_id.is_some() {
            condition_fragments.push(self.prepare_relationship_id_filter(PARENT_ID_FILTER_SQL));
        }
        for (idx, condition) in self.conditions.iter().enumerate() {
            condition_fragments.push(condition.to_query_fragment(idx));
        }
        let mut query_sql = base_query.to_string();
        if !condition_fragments.is_empty() {
            query_sql.push_str(&format!(" WHERE {}", condition_fragments.join(" AND ")));
        }
        if let Some(limit) = self.limit {
            query_sql.push_str(&format!(" LIMIT {}", limit));
        }
        query_sql
    }

    fn prepare_relationship_id_filter(&self, condition_part: &str) -> String {
        // Note that for simplicity's sake, we are appending the right parent of the subquery there.
        if self.relationship_kind.is_some() {
            format!("{} AND kind = :relationship_kind)", condition_part)
        } else {
            format!("{})", condition_part)
        }
    }

    pub fn to_query_params(&self) -> Vec<(String, &dyn ToSql)> {
        let mut params: Vec<(String, &dyn ToSql)> = if self.has_interest_rectangle {
            vec![
                (":min_x".to_string(), &self.min_x),
                (":max_x".to_string(), &self.max_x),
                (":min_y".to_string(), &self.min_y),
                (":max_y".to_string(), &self.max_y),
            ]
        } else {
            vec![]
        };
        for (idx, discriminator) in self.included_discriminators.iter().enumerate() {
            params.push((format!(":included_discriminator{}", idx), discriminator));
        }
        for (idx, discriminator) in self.excluded_discriminators.iter().enumerate() {
            params.push((format!(":excluded_discriminator{}", idx), discriminator));
        }
        if self.child_id.is_some() {
            params.push((":parent_id".to_string(), self.child_id.as_ref().unwrap()));
        }
        if self.parent_id.is_some() {
            params.push((":child_id".to_string(), self.parent_id.as_ref().unwrap()));
        }
        if self.relationship_kind.is_some() {
            params.push((
                ":relationship_kind".to_string(),
                self.relationship_kind.as_ref().unwrap(),
            ));
        }
        for (idx, condition) in self.conditions.iter().enumerate() {
            if let Some(mut vals) = condition.to_param_values(idx) {
                params.append(&mut vals);
            }
        }
        params
    }
}
