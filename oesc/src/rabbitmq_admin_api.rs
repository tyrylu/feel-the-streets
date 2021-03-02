use anyhow::Result;
use serde::Deserialize;
use std::collections::HashMap;
use url::Url;

#[derive(Deserialize)]
pub struct ExchangeBinding {
    pub source: String,
    pub vhost: String,
    pub destination: String,
    pub destination_type: String,
    pub routing_key: String,
    pub arguments: HashMap<String, String>,
    pub properties_key: String,
}

pub struct Client {
    rabbitmq_http_api_base: Url,
}

impl Client {
    pub fn new(rabbitmq_management_uri: String) -> Result<Self> {
        Ok(Client {
            rabbitmq_http_api_base: Url::parse(&rabbitmq_management_uri)?.join("/api/")?,
        })
    }

    pub fn get_queues_bound_to_exchange(
        &self,
        vhost: &str,
        exchange: &str,
    ) -> Result<Vec<ExchangeBinding>> {
        let final_url = self
            .rabbitmq_http_api_base
            .join(&format!("exchanges/{}/{}/bindings/source", vhost, exchange))?;
        Ok(ureq::get(final_url.as_str()).call()?.into_json()?)
    }
}
