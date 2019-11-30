use structopt::StructOpt;
use anyhow::Result;

mod command;
mod change_field_type;
mod remove_field;

use command::Command;
fn main() -> Result<()> {
    let cmd = Command::from_args();
    match cmd {
        Command::ChangeFieldType { entity, field, new_type, force} => change_field_type::change_field_type(entity, field, new_type, force),
        Command::RemoveField { entity, field, new_name} => remove_field::remove_field(entity, field, new_name)
    }
}
