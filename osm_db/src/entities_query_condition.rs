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
pub enum FieldCondition {
    Concrete {
        field: String,
        condition: Condition,
    },
    Or {
        left: Box<FieldCondition>,
        right: Box<FieldCondition>,
    },
}

impl FieldCondition {
    pub fn new(field: String, condition: Condition) -> Self {
        Self::Concrete { field, condition }
    }

    pub fn to_query_fragment(&self, condition_index: usize) -> String {
        self.to_query_fragment_internal(condition_index.to_string())
    }

    fn to_query_fragment_internal(&self, condition_placeholder_base: String) -> String {
        match self {
            Self::Concrete { field, condition } => {
                let field_expr = format!("json_extract(data, '$.{field}')");
                let operation = match condition {
                    Condition::IsNull => "IS NULL".to_string(),
                    Condition::IsNotNull => "IS NOT NULL".to_string(),
                    Condition::Eq { .. } => format!("= :param{condition_placeholder_base}"),
                    Condition::Neq { .. } => format!("!= :param{condition_placeholder_base}"),
                    Condition::Lt { .. } => format!("< :param{condition_placeholder_base}"),
                    Condition::Le { .. } => format!("<= :param{condition_placeholder_base}"),
                    Condition::Gt { .. } => format!("> :param{condition_placeholder_base}"),
                    Condition::Ge { .. } => format!(">= :param{condition_placeholder_base}"),
                    Condition::Like { .. } => format!("LIKE :param{condition_placeholder_base}"),
                };
                format!("{field_expr} {operation}")
            }
            Self::Or { left, right } => {
                format!(
                    "({} OR {})",
                    left.to_query_fragment_internal(format!("{condition_placeholder_base}l")),
                    right.to_query_fragment_internal(format!("{condition_placeholder_base}r"))
                )
            }
        }
    }

    pub fn to_param_values(&self, condition_index: usize) -> Option<Vec<(String, &dyn ToSql)>> {
        self.to_param_values_internal(condition_index.to_string())
    }

    fn to_param_values_internal(
        &self,
        condition_placeholder_base: String,
    ) -> Option<Vec<(String, &dyn ToSql)>> {
        match self {
            Self::Concrete { condition, .. } => match &condition {
                Condition::Eq { value }
                | Condition::Neq { value }
                | Condition::Lt { value }
                | Condition::Le { value }
                | Condition::Gt { value }
                | Condition::Ge { value }
                | Condition::Like { value } => Some(vec![(
                    format!(":param{condition_placeholder_base}"),
                    value.as_ref(),
                )]),
                Condition::IsNull | Condition::IsNotNull => None,
            },
            Self::Or { left, right } => {
                match (
                    left.to_param_values_internal(format!("{condition_placeholder_base}l")),
                    right.to_param_values_internal(format!("{condition_placeholder_base}r")),
                ) {
                    (Some(mut left), Some(mut right)) => {
                        left.append(&mut right);
                        Some(left)
                    }
                    (None, Some(right)) => Some(right),
                    (Some(left), None) => Some(left),
                    (None, None) => None,
                }
            }
        }
    }
}
