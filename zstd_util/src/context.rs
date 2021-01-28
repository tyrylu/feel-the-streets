use crate::Result;
use log::trace;
use std::time::Instant;
use zstd_safe::{CCtx, DCtx, CDict};

pub struct ZstdContext<'a> {
    compression_context: CCtx<'a>,
    _compression_dict: Option<CDict<'a>>,
    decompression_context: DCtx<'a>,
}

impl<'a> ZstdContext<'a> {
    pub fn new(compression_level: i32, dictionary: Option<&[u8]>) -> Self {
        let mut cctx = zstd_safe::create_cctx();
        let mut dctx = zstd_safe::create_dctx();
        let cdict = match dictionary {
            Some(ref dict_data) => {
                let dict = zstd_safe::create_cdict(&dict_data, compression_level);
                zstd_safe::cctx_ref_cdict(&mut cctx, &dict).expect("Failed to associate compression dictionary");
                Some(dict)
            },
            None => None
        };
        if let Some(ref dict_data) = dictionary {
                            zstd_safe::dctx_load_dictionary(&mut dctx, &dict_data).expect("Failed to associate decompression dictionary");
        }
        Self { compression_context: cctx, decompression_context: dctx, _compression_dict: cdict}
    }

    pub fn compress(&mut self, data: &[u8]) -> Result<Vec<u8>> {
        let mut compressed = Vec::new();
        compressed.resize(data.len(), 0);
        let start = Instant::now();
        let compressed_size = zstd_safe::compress2(&mut self.compression_context, &mut compressed, &data)?;
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
        zstd_safe::decompress_dctx(&mut self.decompression_context, &mut original, &compressed)?;
        trace!("Decompressed {} to {} bytes in {:?}.", compressed.len(), original.len(), start.elapsed());
        Ok(original)
    }
    
}