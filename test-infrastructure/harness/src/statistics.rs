use crate::metrics::{AggregatedMetrics, Metrics, MetricStats};
use serde::{Deserialize, Serialize};

/// Statistical analysis of performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Statistics {
    pub parse_time: MetricStats,
    pub layout_time: MetricStats,
    pub paint_time: MetricStats,
    pub total_time: MetricStats,
    pub memory: MetricStats,
}

impl Statistics {
    /// Compute statistics from a list of metrics
    pub fn from_metrics(metrics: &[Metrics]) -> Self {
        let parse_times: Vec<f64> = metrics.iter().map(|m| m.parse_time_ms).collect();
        let layout_times: Vec<f64> = metrics.iter().map(|m| m.layout_time_ms).collect();
        let paint_times: Vec<f64> = metrics.iter().map(|m| m.paint_time_ms).collect();
        let total_times: Vec<f64> = metrics.iter().map(|m| m.total_time_ms).collect();
        let memory_values: Vec<f64> = metrics.iter().map(|m| m.memory_mb).collect();

        Self {
            parse_time: MetricStats::from_values(parse_times),
            layout_time: MetricStats::from_values(layout_times),
            paint_time: MetricStats::from_values(paint_times),
            total_time: MetricStats::from_values(total_times),
            memory: MetricStats::from_values(memory_values),
        }
    }

    /// Print statistics in human-readable format
    pub fn print(&self) {
        println!("  Parse Time:   mean={:.2}ms  median={:.2}ms  p95={:.2}ms  p99={:.2}ms",
                 self.parse_time.mean, self.parse_time.median, 
                 self.parse_time.p95, self.parse_time.p99);
        println!("  Layout Time:  mean={:.2}ms  median={:.2}ms  p95={:.2}ms  p99={:.2}ms",
                 self.layout_time.mean, self.layout_time.median,
                 self.layout_time.p95, self.layout_time.p99);
        println!("  Paint Time:   mean={:.2}ms  median={:.2}ms  p95={:.2}ms  p99={:.2}ms",
                 self.paint_time.mean, self.paint_time.median,
                 self.paint_time.p95, self.paint_time.p99);
        println!("  Total Time:   mean={:.2}ms  median={:.2}ms  p95={:.2}ms  p99={:.2}ms",
                 self.total_time.mean, self.total_time.median,
                 self.total_time.p95, self.total_time.p99);
        println!("  Memory:       mean={:.2}MB  median={:.2}MB  p95={:.2}MB  p99={:.2}MB",
                 self.memory.mean, self.memory.median,
                 self.memory.p95, self.memory.p99);
    }
}

/// Regression detected by baseline comparison
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Regression {
    pub renderer: String,
    pub metric: String,
    pub baseline_value: f64,
    pub current_value: f64,
    pub percent_change: f64,
}

/// Comparison result against baseline
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BaselineComparison {
    pub baseline_commit: String,
    pub baseline_timestamp: chrono::DateTime<chrono::Utc>,
    pub improvements: Vec<Regression>,
    pub regressions: Vec<Regression>,
}

/// Perform Welch's t-test for statistical significance
pub fn welch_t_test(sample1: &[f64], sample2: &[f64]) -> (f64, f64) {
    let n1 = sample1.len() as f64;
    let n2 = sample2.len() as f64;

    let mean1: f64 = sample1.iter().sum::<f64>() / n1;
    let mean2: f64 = sample2.iter().sum::<f64>() / n2;

    let var1: f64 = sample1
        .iter()
        .map(|x| (x - mean1).powi(2))
        .sum::<f64>()
        / (n1 - 1.0);

    let var2: f64 = sample2
        .iter()
        .map(|x| (x - mean2).powi(2))
        .sum::<f64>()
        / (n2 - 1.0);

    let t = (mean1 - mean2) / ((var1 / n1) + (var2 / n2)).sqrt();

    // Degrees of freedom (Welch-Satterthwaite equation)
    let df = ((var1 / n1) + (var2 / n2)).powi(2)
        / ((var1 / n1).powi(2) / (n1 - 1.0) + (var2 / n2).powi(2) / (n2 - 1.0));

    (t, df)
}

/// Calculate coefficient of variation
pub fn coefficient_of_variation(values: &[f64]) -> f64 {
    let mean: f64 = values.iter().sum::<f64>() / values.len() as f64;
    let variance: f64 = values
        .iter()
        .map(|x| (x - mean).powi(2))
        .sum::<f64>()
        / values.len() as f64;
    let std_dev = variance.sqrt();

    (std_dev / mean) * 100.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_statistics_from_metrics() {
        let metrics = vec![
            Metrics {
                parse_time_ms: 10.0,
                layout_time_ms: 20.0,
                paint_time_ms: 15.0,
                total_time_ms: 45.0,
                memory_mb: 50.0,
            },
            Metrics {
                parse_time_ms: 12.0,
                layout_time_ms: 22.0,
                paint_time_ms: 16.0,
                total_time_ms: 50.0,
                memory_mb: 52.0,
            },
            Metrics {
                parse_time_ms: 11.0,
                layout_time_ms: 21.0,
                paint_time_ms: 15.5,
                total_time_ms: 47.5,
                memory_mb: 51.0,
            },
        ];

        let stats = Statistics::from_metrics(&metrics);
        assert!(stats.total_time.mean > 40.0 && stats.total_time.mean < 50.0);
    }

    #[test]
    fn test_coefficient_of_variation() {
        let values = vec![10.0, 12.0, 11.0, 13.0, 10.5];
        let cv = coefficient_of_variation(&values);
        assert!(cv > 0.0 && cv < 100.0);
    }
}
