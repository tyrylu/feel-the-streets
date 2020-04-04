use rusqlite::types::ToSql;
use std::rc::Rc;

#[derive(Clone)]
pub enum Condition {
    IsNull,
    IsNotNull,
    Eq { value: Rc<dyn ToSql> },
    Neq { value: Rc<dyn ToSql> },
    Lt { value: Rc<dyn ToSql> },
    Le { value: Rc<dyn ToSql> },
    Gt { value: Rc<dyn ToSql> },
    Ge { value: Rc<dyn ToSql> },
    Like { value: Rc<dyn ToSql> },
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
