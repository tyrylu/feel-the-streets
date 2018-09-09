error_chain! {
    foreign_links {
        Reqwest(::reqwest::Error);
        Io(::std::io::Error);
    }
}
