use serde::{Deserialize, Serialize};

/// Performance metrics for a single render operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metrics {
    pub parse_time_ms: f64,
    pub layout_time_ms: f64,
    pub paint_time_ms: f64,
    pub total_time_ms: f64,
    pub memory_mb: f64,
}

/// Statistical summary for a single metric
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricStats {
    pub mean: f64,
    pub median: f64,
    pub std_dev: f64,
    pub min: f64,
    pub max: f64,
    pub p95: f64,
    pub p99: f64,
}

impl MetricStats {
    /// Compute statistics from a list of values
    pub fn from_values(mut values: Vec<f64>) -> Self {
        values.sort_by(|a, b| a.partial_cmp(b).unwrap());
        
        let count = values.len() as f64;
        let sum: f64 = values.iter().sum();
        let mean = sum / count;
        
        let median = if values.len() % 2 == 0 {
            let mid = values.len() / 2;
            (values[mid - 1] + values[mid]) / 2.0
        } else {
            values[values.len() / 2]
        };
        
        let variance: f64 = values
            .iter()
            .map(|v| {
                let diff = v - mean;
                diff * diff
            })
            .sum::<f64>()
            / count;
        let std_dev = variance.sqrt();
        
        let min = values[0];
        let max = values[values.len() - 1];
        
        let p95_idx = ((values.len() as f64 * 0.95) as usize).min(values.len() - 1);
        let p99_idx = ((values.len() as f64 * 0.99) as usize).min(values.len() - 1);
        let p95 = values[p95_idx];
        let p99 = values[p99_idx];
        
        Self {
            mean,
            median,
            std_dev,
            min,
            max,
            p95,
            p99,
        }
    }
}
