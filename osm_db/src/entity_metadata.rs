use crate::file_finder;
use std::collections::HashMap;
use std::fs::File;

type EnumMap = HashMap<String, HashMap<String, i32>>;
type RawEntityMetadataMap = HashMap<String, RawEntityMetadata>;

lazy_static! {
    static ref RAW_METADATA_MAP: RawEntityMetadataMap = {

        let entities_file = file_finder::find_file_in_current_or_exe_dir("entities.yml").expect("Could not find entities.yml");
        let fp = File::open(entities_file).expect("Could not open entity definition file.");
        serde_yaml::from_reader::<_, RawEntityMetadataMap>(fp).unwrap()
    };
    static ref ENUM_MAP: EnumMap = {
        let enums_file = file_finder::find_file_in_current_or_exe_dir("enums.yml").expect("Could not find enums.yml");        
        let fp = File::open(enums_file).expect("Could not open enums definition file.");
        serde_yaml::from_reader::<_, EnumMap>(fp).unwrap()
    };
}

pub fn all_known_discriminators() -> Vec<&'static String> {
    RAW_METADATA_MAP.keys().collect()
}

#[derive(Deserialize)]
struct RawEntityMetadata {
    inherits: Option<String>,
    long_display_template: Option<String>,
    short_display_template: Option<String>,
    fields: HashMap<String, String>,
}

impl RawEntityMetadata {
    fn for_discriminator(discriminator: &str) -> Option<&Self> {
        RAW_METADATA_MAP.get(discriminator)
    }
}

#[derive(Clone)]
pub struct Field {
    pub type_name: String,
    pub required: bool,
}

pub struct EntityMetadata {
    pub discriminator: String,
    pub long_display_template: Option<String>,
    pub short_display_template: Option<String>,
    inherits: Option<String>,
    pub fields: HashMap<String, Field>,
}

impl EntityMetadata {
    pub fn for_discriminator(discriminator: &str) -> Option<Self> {
        let raw = RawEntityMetadata::for_discriminator(discriminator)?;
        let mut fields = HashMap::with_capacity(raw.fields.len());
        for (name, type_name) in &raw.fields {
            let required = type_name.starts_with('!');
            let start = if required { 1 } else { 0 };
            fields.insert(
                name.to_string(),
                Field {
                    type_name: type_name[start..].to_string(),
                    required,
                },
            );
        }
        Some(Self {
            fields,
            long_display_template: raw.long_display_template.clone(),
            short_display_template: raw.short_display_template.clone(),
            inherits: raw.inherits.clone(),
            discriminator: discriminator.to_string(),
        })
    }

    pub fn parent_metadata(&self) -> Option<Self> {
        EntityMetadata::for_discriminator(&self.inherits.clone()?)
    }
    pub fn all_fields(&self) -> HashMap<String, Field> {
        let mut ret = self.fields.clone();
        if let Some(parent) = self.parent_metadata() {
            ret.extend(parent.all_fields());
        }
        ret
    }
}

pub struct Enum {
    pub name: String,
    members: &'static HashMap<String, i32>,
    reverse_members: HashMap<&'static i32, &'static String>,
}

impl Enum {
    pub fn all_known() -> Vec<&'static String> {
        ENUM_MAP.keys().collect()
    }

    pub fn with_name(name: &str) -> Option<Self> {
        let members = ENUM_MAP.get(name)?;
        let mut reverse = HashMap::new();
        for (key, val) in members.iter() {
            reverse.insert(val, key);
        }
        Some(Self {
            name: name.to_string(),
            reverse_members: reverse,
            members,
        })
    }

    pub fn value_for_name(&self, name: &str) -> Option<&i32> {
        self.members.get(name)
    }

    pub fn name_for_value(&self, value: i32) -> Option<&'static String> {
        self.reverse_members.get(&value).copied()
    }
}
