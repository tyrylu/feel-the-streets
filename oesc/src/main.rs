use anyhow::Result;
use structopt::StructOpt;

mod change_field_type;
mod command;
mod remove_field;
mod view_field_usage;

use command::Command;
fn main() -> Result<()> {
    let cmd = Command::from_args();
    match cmd {
        Command::ChangeFieldType {
            entity,
            field,
            new_type,
            force,
        } => change_field_type::change_field_type(entity, field, new_type, force),
        Command::RemoveField {
            entity,
            field,
            new_name,
        } => remove_field::remove_field(entity, field, new_name),
        Command::ViewFieldUsage { entity, field } => {
            view_field_usage::view_field_usage(entity, field)
        }
    }
}
