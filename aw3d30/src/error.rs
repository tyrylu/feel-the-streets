#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("HTTP error: {0}")]
    Http(#[from] ureq::Error),
    #[error("Zip related error: {0}")]
    Zip(#[from] zip::result::ZipError),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Tiff error: {0}")]
    Tiff(#[from] tiff::TiffError),
    #[error("Map serialization error: {0}")]
    MapSerialization(#[from] bincode::Error),
    #[error("Invalid archive filename {0}")]
    InvalidArchiveFilename(String),
    #[error("Unexpected pixel format")]
    UnexpectedPixelFormat,
}
