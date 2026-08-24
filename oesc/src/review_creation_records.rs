use anyhow::Result;
use osm_db::translation::record::TranslationRecord;
use std::fs::File;
use std::io::BufReader;
use std::path::PathBuf;

const RECORDS_DIR: &str = "creation_records";
const EXAMPLE_LIMIT: usize = 5;

pub fn review_creation_records(min_count: u32, category: Option<String>) -> Result<()> {
    let mut aggregate = TranslationRecord::new();

    let dir = PathBuf::from(RECORDS_DIR);
    let mut files_loaded = 0u32;
    for entry in std::fs::read_dir(&dir)? {
        let entry = entry?;
        let path = entry.path();
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or_default();
        if name.starts_with("creation_") && name.ends_with(".json") {
            let f = File::open(&path)?;
            let reader = BufReader::new(f);
            let record: TranslationRecord = serde_json::from_reader(reader)?;
            record.merge_to(&mut aggregate);
            files_loaded += 1;
        }
    }

    println!("Loaded {files_loaded} creation records.\n");

    let summary = aggregate.summarize();
    let min = min_count as usize;
    let show_all = category.is_none();

    let cat = category.as_deref().unwrap_or("");

    // --- Missing enum members ---
    if show_all || cat == "enum" {
        let items: Vec<_> = summary
            .missing_enum_members
            .iter()
            .filter(|e| e.count >= min)
            .collect();
        println!("=== Missing enum members ({} items) ===", items.len());
        if items.is_empty() {
            println!("  (none above threshold)");
        }
        for entry in &items {
            println!("  {:<50} {}", entry.key, entry.count);
        }
        println!();
    }

    // --- Type violations ---
    if show_all || cat == "type" {
        let items: Vec<_> = summary
            .type_violations
            .iter()
            .filter(|e| e.count >= min)
            .collect();
        println!("=== Type violations ({} items) ===", items.len());
        if items.is_empty() {
            println!("  (none above threshold)");
        }
        for entry in &items {
            let examples = entry.examples[..entry.examples.len().min(EXAMPLE_LIMIT)]
                .iter()
                .map(|v| format!("\"{v}\""))
                .collect::<Vec<_>>()
                .join(", ");
            println!("  {} ({}): {}", entry.key, entry.count, examples);
        }
        println!();
    }

    // --- Unknown fields ---
    if show_all || cat == "fields" {
        let items: Vec<_> = summary
            .unknown_fields
            .iter()
            .filter(|e| e.count >= min)
            .collect();
        println!("=== Unknown fields ({} items) ===", items.len());
        if items.is_empty() {
            println!("  (none above threshold)");
        }
        for entry in &items {
            let examples = entry.examples[..entry.examples.len().min(EXAMPLE_LIMIT)]
                .iter()
                .map(|v| format!("\"{v}\""))
                .collect::<Vec<_>>()
                .join(", ");
            println!("  {} ({}): {}", entry.key, entry.count, examples);
        }
        println!();
    }

    // --- Missing required fields ---
    if show_all || cat == "required" {
        let items: Vec<_> = summary
            .missing_required_fields
            .iter()
            .filter(|e| e.count >= min)
            .collect();
        println!(
            "=== Missing required fields / entities dropped ({} items) ===",
            items.len()
        );
        if items.is_empty() {
            println!("  (none above threshold)");
        }
        for entry in &items {
            println!("  {:<50} {}", entry.key, entry.count);
        }
        println!();
    }

    // --- Potentially interesting objects ---
    if show_all || cat == "interesting" {
        let items: Vec<_> = summary
            .interesting_object_combinations
            .iter()
            .filter(|e| e.count >= min)
            .collect();
        println!(
            "=== Potentially interesting object tag combinations ({} items) ===",
            items.len()
        );
        if items.is_empty() {
            println!("  (none above threshold)");
        }
        for entry in &items {
            println!("  ({}) {}", entry.count, entry.key);
        }
        println!();
    }

    Ok(())
}
