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

/// Trait for collecting performance metrics
pub trait PerformanceMetrics {
    /// Get parse time in milliseconds
    fn parse_time(&self) -> f64;
    
    /// Get layout time in milliseconds
    fn layout_time(&self) -> f64;
    
    /// Get paint time in milliseconds
    fn paint_time(&self) -> f64;
    
    /// Get total render time in milliseconds
    fn total_time(&self) -> f64;
    
    /// Get memory usage in bytes
    fn memory_usage(&self) -> usize;
}

impl PerformanceMetrics for Metrics {
    fn parse_time(&self) -> f64 {
        self.parse_time_ms
    }
    
    fn layout_time(&self) -> f64 {
        self.layout_time_ms
    }
    
    fn paint_time(&self) -> f64 {
        self.paint_time_ms
    }
    
    fn total_time(&self) -> f64 {
        self.total_time_ms
    }
    
    fn memory_usage(&self) -> usize {
        (self.memory_mb * 1_048_576.0) as usize
    }
}

/// Aggregated metrics across multiple runs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregatedMetrics {
    pub parse_time: MetricStats,
    pub layout_time: MetricStats,
    pub paint_time: MetricStats,
    pub total_time: MetricStats,
    pub memory: MetricStats,
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
