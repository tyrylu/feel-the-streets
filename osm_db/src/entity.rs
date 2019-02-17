pub struct Entity {
    pub id: i32,
    pub geometry: String,
    pub discriminator: String,
    pub data: String,
    pub effective_width: Option<f64>,
}

pub struct NotStoredEntity {
    pub geometry: String,
    pub discriminator: String,
    pub data: String,
    pub effective_width: Option<f64>,
}
