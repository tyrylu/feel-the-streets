use std::env;
use std::path::PathBuf; 

pub fn find_file_in_current_or_exe_dir(name: &str) -> Option<PathBuf> {
    let mut exe_dir_attempt = env::current_exe().expect("Could not determine current exe");
    exe_dir_attempt.set_file_name(name);
    if exe_dir_attempt.exists() {
        return Some(exe_dir_attempt);
    }
    let mut current_dir_attempt = env::current_dir().expect("Could not determine current directory");
    current_dir_attempt.push(name);
    if current_dir_attempt.exists() {
        return Some(current_dir_attempt);
    }
    None
}