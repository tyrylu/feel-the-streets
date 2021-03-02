use crate::Result;
use log::trace;
use std::time::Instant;
use zstd_safe::{CCtx, CDict, CParameter, DCtx};

pub struct ZstdContext<'a> {
    compression_context: CCtx<'a>,
    _compression_dict: Option<CDict<'a>>,
    decompression_context: DCtx<'a>,
}

impl<'a> ZstdContext<'a> {
    pub fn new(compression_level: i32, dictionary: Option<&[u8]>) -> Self {
        let mut cctx = CCtx::create();
        let mut dctx = DCtx::create();
        let cdict = match dictionary {
            Some(ref dict_data) => {
                let dict = CDict::create(&dict_data, compression_level);
                cctx.ref_cdict(&dict)
                    .expect("Failed to associate compression dictionary");
                Some(dict)
            }
            None => {
                cctx.set_parameter(CParameter::CompressionLevel(compression_level))
                    .expect("Failed to se the compression level");
                None
            }
        };
        if let Some(ref dict_data) = dictionary {
            dctx.load_dictionary(&dict_data)
                .expect("Failed to associate decompression dictionary");
        }
        Self {
            compression_context: cctx,
            decompression_context: dctx,
            _compression_dict: cdict,
        }
    }

    pub fn compress(&mut self, data: &[u8]) -> Result<Vec<u8>> {
        let mut compressed = Vec::new();
        compressed.resize(zstd_safe::compress_bound(data.len()), 0);
        let start = Instant::now();
        let compressed_size = self.compression_context.compress2(&mut compressed, &data)?;
        compressed.resize(compressed_size as usize, 0);
        trace!(
            "Compressed {} to {} bytes in {:?}.",
            data.len(),
            compressed.len(),
            start.elapsed()
        );
        Ok(compressed)
    }

    pub fn decompress(&mut self, compressed: &[u8]) -> Result<Vec<u8>> {
        let mut original = Vec::new();
        original.resize(zstd_safe::get_frame_content_size(&compressed) as usize, 0);
        let start = Instant::now();
        self.decompression_context
            .decompress(&mut original, &compressed)?;
        trace!(
            "Decompressed {} to {} bytes in {:?}.",
            compressed.len(),
            original.len(),
            start.elapsed()
        );
        Ok(original)
    }
}
