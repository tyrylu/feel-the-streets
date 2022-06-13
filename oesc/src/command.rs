use clap::{Parser, Subcommand};

#[derive(Parser)]
pub struct Args {
    #[clap(subcommand)]
    pub command: Command,
}

#[derive(Subcommand, Debug)]
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
        #[clap(long)]
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
    /// Forces a redownload of the given areas or all of them.
    RequestRedownload {
        /// Request redownload for all areas
        #[clap(long, conflicts_with = "area")]
        all: bool,
        /// Request redownload for a specific area
        #[clap(long, conflicts_with = "all")]
        area: Option<i64>,
    },
    /// Creates a frozen copy of the current state of an area.
    CreateFrozenCopy {
        /// The id of the original area.
        area_id: i64,
        /// The human readable name of the new copy.
        new_name: String,
    },
    /// Regenerates the parent osm ids for all areas.
    RegenerateParentOSMIds,
}
