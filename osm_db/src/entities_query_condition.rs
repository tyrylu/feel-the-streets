use rusqlite::types::ToSql;
use std::sync::Arc;

#[derive(Clone)]
pub enum Condition {
    IsNull,
    IsNotNull,
    Eq { value: Arc<dyn ToSql + Send + Sync> },
    Neq { value: Arc<dyn ToSql + Send + Sync> },
    Lt { value: Arc<dyn ToSql + Send + Sync> },
    Le { value: Arc<dyn ToSql + Send + Sync> },
    Gt { value: Arc<dyn ToSql + Send + Sync> },
    Ge { value: Arc<dyn ToSql + Send + Sync> },
    Like { value: Arc<dyn ToSql + Send + Sync> },
}

#[derive(Clone)]
pub struct FieldCondition {
    pub field: String,
    pub condition: Condition,
}

impl FieldCondition {
    pub fn new(field: String, condition: Condition) -> Self {
        Self { field, condition }
    }
    pub fn to_query_fragment(&self, condition_index: usize) -> String {
        let field_expr = format!("json_extract(data, '$.{}')", self.field);
        let operation = match self.condition {
            Condition::IsNull => "IS NULL".to_string(),
            Condition::IsNotNull => "IS NOT NULL".to_string(),
            Condition::Eq { .. } => format!("= :param{}", condition_index),
            Condition::Neq { .. } => format!("!= :param{}", condition_index),
            Condition::Lt { .. } => format!("< :param{}", condition_index),
            Condition::Le { .. } => format!("<= :param{}", condition_index),
            Condition::Gt { .. } => format!("> :param{}", condition_index),
            Condition::Ge { .. } => format!(">= :param{}", condition_index),
            Condition::Like { .. } => format!("LIKE :param{}", condition_index),
        };
        format!("{} {}", field_expr, operation)
    }

    pub fn to_param_value(&self) -> Option<&dyn ToSql> {
        match &self.condition {
            Condition::Eq { value }
            | Condition::Neq { value }
            | Condition::Lt { value }
            | Condition::Le { value }
            | Condition::Gt { value }
            | Condition::Ge { value }
            | Condition::Like { value } => Some(value.as_ref()),
            Condition::IsNull | Condition::IsNotNull => None,
        }
    }
}
