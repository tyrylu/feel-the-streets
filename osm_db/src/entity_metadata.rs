use crate::file_finder;
use indexmap::IndexMap;
use once_cell::sync::Lazy;
use serde::Deserialize;
use std::collections::HashMap;
use std::fs::File;

type EnumMap = HashMap<String, IndexMap<String, i32>>;
type RawEntityMetadataMap = HashMap<String, RawEntityMetadata>;

static RAW_METADATA_MAP: Lazy<RawEntityMetadataMap> = Lazy::new(|| {
    let entities_file = file_finder::find_file_in_current_or_exe_dir("entities.yml")
        .expect("Could not find entities.yml");
    let fp = File::open(entities_file).expect("Could not open entity definition file.");
    serde_yaml::from_reader::<_, RawEntityMetadataMap>(fp).unwrap()
});
static ENUM_MAP: Lazy<EnumMap> = Lazy::new(|| {
    let enums_file = file_finder::find_file_in_current_or_exe_dir("enums.yml")
        .expect("Could not find enums.yml");
    let fp = File::open(enums_file).expect("Could not open enums definition file.");
    serde_yaml::from_reader::<_, EnumMap>(fp).unwrap()
});
static METADATA_MAP: Lazy<HashMap<&'static str, EntityMetadata>> = Lazy::new(|| {
    let mut ret = HashMap::with_capacity(RAW_METADATA_MAP.len());
    for (name, raw) in RAW_METADATA_MAP.iter() {
        let mut fields = IndexMap::with_capacity(raw.fields.len());
        for (name, type_name) in &raw.fields {
            let required = type_name.starts_with('!');
            let start = if required { 1 } else { 0 };
            fields.insert(
                name,
                Field {
                    type_name: &type_name[start..],
                    required,
                },
            );
        }
        ret.insert(name.as_str(), EntityMetadata {
            fields,
            long_display_template: &raw.long_display_template,
            short_display_template: &raw.short_display_template,
            inherits: &raw.inherits,
            discriminator: name,
        });
    }
    ret
});

pub fn all_known_discriminators() -> Vec<&'static String> {
    RAW_METADATA_MAP.keys().collect()
}

#[derive(Deserialize)]
struct RawEntityMetadata {
    inherits: Option<String>,
    long_display_template: Option<String>,
    short_display_template: Option<String>,
    fields: IndexMap<String, String>,
}

#[derive(Clone)]
pub struct Field {
    pub type_name: &'static str,
    pub required: bool,
}

pub struct EntityMetadata {
    pub discriminator: &'static str,
    pub long_display_template: &'static Option<String>,
    pub short_display_template: &'static Option<String>,
    inherits: &'static Option<String>,
    pub fields: IndexMap<&'static String, Field>,
}

impl EntityMetadata {
    pub fn for_discriminator(discriminator: &str) -> Option<&'static Self> {
        METADATA_MAP.get(discriminator)
            }

    pub fn parent_metadata(&self) -> Option<&Self> {
        match self.inherits {
            None => None,
            Some(val) => EntityMetadata::for_discriminator(val)
        }
    }
    
    pub fn all_fields(&self) -> IndexMap<&'static String, Field> {
        let mut ret = self.fields.clone();
        if let Some(parent) = self.parent_metadata() {
            ret.extend(parent.all_fields());
        }
        ret
    }
}

pub struct Enum {
    pub name: String,
    pub members: &'static IndexMap<String, i32>,
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
