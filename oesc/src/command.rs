use structopt::StructOpt;

#[derive(StructOpt)]
pub enum Command {
    /// Changes an entity field's type. Note that it must be run in production where the area databases are stored, so it can actually do the changes. In addition, the entities.yml file must be modified manually.
    ChangeFieldType {
        /// The entity to change the field type for.
        entity: String,
        /// The field upon which the change should be executed.
        field: String,
        /// The new type for the field. Note that the conversions must all pass before the change will be actually executed.
        new_type: String,
        /// If specified, ignores the type conversion failures and continues nonetheless.
        #[structopt(long)]
        force: bool,
    },
    RemoveField {
        /// The entity type to operate against.
        entity: String,
        /// The field to remove.
        field: String,
        /// The new name for the field, if specified, the removal is actually a rename.
        new_name: Option<String>,
    },
    /// Shows a summary with the current values of a given field.
    ViewFieldUsage {
        /// The entity to process.
        entity: String,
        /// The field to display statistics about.
        field: String,
    },
}
