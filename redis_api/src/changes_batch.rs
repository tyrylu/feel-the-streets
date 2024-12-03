use crate::changes_stream::ChangesStream;
use crate::Result;
use osm_db::semantic_change::SemanticChange;

pub struct ChangesBatch<'a> {
    stream: &'a mut ChangesStream,
    num_changes: u64,
}

impl<'a> ChangesBatch<'a> {
    pub(crate) fn for_stream(stream: &'a mut ChangesStream) -> Self {
        Self {
            stream,
            num_changes: 0,
        }
    }

    pub fn add_change(&mut self, change: &SemanticChange) -> Result<()> {
        match self.stream.add_change(change) {
            Ok(()) => {
                self.num_changes += 1;
                Ok(())
            }
            Err(e) => Err(e),
        }
    }
}

impl Drop for ChangesBatch<'_> {
    fn drop(&mut self) {
        self.stream
            .increment_changes_count_by(self.num_changes)
            .expect("Could not increment changes count")
    }
}
