use anyhow::{Context, Result};
use rand::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;
use tracing::{debug, info};

use crate::metrics::Metrics;
use crate::renderers::{RenderEngine, RendererType};
use crate::statistics::{BaselineComparison, Regression, Statistics};

/// Represents a test page with varying complexity
#[derive(Debug, Clone)]
pub struct TestPage {
    pub name: String,
    pub html: String,
    pub complexity: PageComplexity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PageComplexity {
    pub dom_depth: usize,
    pub element_count: usize,
    pub css_rules: usize,
}

/// Viewport dimensions for testing
#[derive(Debug, Clone, Copy)]
pub struct Viewport {
    pub width: u32,
    pub height: u32,
}

impl Viewport {
    pub fn random() -> Self {
        let mut rng = thread_rng();
        // Common viewport sizes
        let sizes = [
            (320, 568),   // iPhone SE
            (375, 667),   // iPhone 8
            (414, 896),   // iPhone 11 Pro Max
            (768, 1024),  // iPad Portrait
            (1024, 768),  // iPad Landscape
            (1280, 720),  // HD
            (1920, 1080), // Full HD
            (2560, 1440), // QHD
        ];
        let (width, height) = sizes[rng.gen_range(0..sizes.len())];
        Self { width, height }
    }
}

/// Monte Carlo test runner
pub struct MonteCarloTest {
    iterations: usize,
    test_pages: Vec<TestPage>,
    enabled_renderers: Vec<RendererType>,
}

impl MonteCarloTest {
    /// Create a new Monte Carlo test suite
    pub fn new(iterations: usize, pages_dir: PathBuf) -> Result<Self> {
        let test_pages = Self::load_test_pages(&pages_dir)?;
        
        if test_pages.is_empty() {
            anyhow::bail!("No test pages found in {}", pages_dir.display());
        }

        info!("Loaded {} test pages", test_pages.len());

        Ok(Self {
            iterations,
            test_pages,
            enabled_renderers: Vec::new(),
        })
    }

    /// Enable a specific renderer for testing
    pub fn enable_renderer(&mut self, renderer: &str) {
        let renderer_type = match renderer.to_lowercase().as_str() {
            "rustkit" => RendererType::RustKit,
            "webkit" => RendererType::WebKit,
            "blink" => RendererType::Blink,
            "gecko" => RendererType::Gecko,
            _ => {
                tracing::warn!("Unknown renderer: {}", renderer);
                return;
            }
        };
        
        if !self.enabled_renderers.contains(&renderer_type) {
            self.enabled_renderers.push(renderer_type);
        }
    }

    /// Load test pages from directory
    fn load_test_pages(dir: &PathBuf) -> Result<Vec<TestPage>> {
        let mut pages = Vec::new();

        // Load manifest if it exists
        let manifest_path = dir.join("manifest.json");
        if manifest_path.exists() {
            let manifest_data = fs::read_to_string(&manifest_path)
                .context("Failed to read manifest.json")?;
            
            #[derive(Deserialize)]
            struct Manifest {
                pages: Vec<ManifestEntry>,
            }
            
            #[derive(Deserialize)]
            struct ManifestEntry {
                file: String,
                name: String,
                complexity: PageComplexity,
            }
            
            let manifest: Manifest = serde_json::from_str(&manifest_data)
                .context("Failed to parse manifest.json")?;
            
            for entry in manifest.pages {
                let page_path = dir.join(&entry.file);
                if page_path.exists() {
                    let html = fs::read_to_string(&page_path)
                        .with_context(|| format!("Failed to read {}", entry.file))?;
                    
                    pages.push(TestPage {
                        name: entry.name,
                        html,
                        complexity: entry.complexity,
                    });
                }
            }
        } else {
            // Fallback: load all .html files
            for entry in fs::read_dir(dir)? {
                let entry = entry?;
                let path = entry.path();
                
                if path.extension().and_then(|s| s.to_str()) == Some("html") {
                    let html = fs::read_to_string(&path)?;
                    let name = path.file_name()
                        .unwrap()
                        .to_string_lossy()
                        .to_string();
                    
                    pages.push(TestPage {
                        name: name.clone(),
                        html,
                        complexity: PageComplexity {
                            dom_depth: 10, // Default values
                            element_count: 100,
                            css_rules: 50,
                        },
                    });
                }
            }
        }

        Ok(pages)
    }

    /// Run the Monte Carlo test suite
    pub fn run(&self) -> Result<TestResults> {
        let start_time = Instant::now();
        let mut rng = thread_rng();
        
        // Initialize results storage
        let mut renderer_results: HashMap<String, Vec<Metrics>> = HashMap::new();
        for renderer in &self.enabled_renderers {
            renderer_results.insert(renderer.to_string(), Vec::new());
        }

        info!("Starting {} iterations...", self.iterations);

        // Run Monte Carlo iterations
        for i in 0..self.iterations {
            if i % 100 == 0 && i > 0 {
                info!("Progress: {}/{} iterations", i, self.iterations);
            }

            // Randomize test conditions
            let page = &self.test_pages[rng.gen_range(0..self.test_pages.len())];
            let viewport = Viewport::random();

            debug!("Iteration {}: page={}, viewport={}x{}", 
                   i, page.name, viewport.width, viewport.height);

            // Test each enabled renderer
            for renderer_type in &self.enabled_renderers {
                let metrics = self.measure_render(renderer_type, page, viewport)?;
                renderer_results
                    .get_mut(&renderer_type.to_string())
                    .unwrap()
                    .push(metrics);
            }
        }

        let total_duration = start_time.elapsed();

        // Compute statistics for each renderer
        let mut statistics_map = HashMap::new();
        for (renderer, metrics_list) in renderer_results {
            let stats = Statistics::from_metrics(&metrics_list);
            statistics_map.insert(renderer, stats);
        }

        Ok(TestResults {
            platform: get_platform(),
            timestamp: chrono::Utc::now(),
            git_commit: get_git_commit().unwrap_or_else(|_| "unknown".to_string()),
            iterations: self.iterations,
            total_duration_secs: total_duration.as_secs_f64(),
            renderers: statistics_map,
            regressions: Vec::new(),
            baseline_comparison: None,
        })
    }

    /// Measure rendering performance for a single page
    fn measure_render(
        &self,
        renderer_type: &RendererType,
        page: &TestPage,
        viewport: Viewport,
    ) -> Result<Metrics> {
        let engine = RenderEngine::create(renderer_type)?;
        
        let start = Instant::now();
        
        // Parse HTML
        let parse_start = Instant::now();
        engine.parse_html(&page.html)?;
        let parse_time = parse_start.elapsed();
        
        // Layout
        let layout_start = Instant::now();
        engine.layout(viewport.width, viewport.height)?;
        let layout_time = layout_start.elapsed();
        
        // Paint
        let paint_start = Instant::now();
        engine.paint()?;
        let paint_time = paint_start.elapsed();
        
        let total_time = start.elapsed();
        let memory_used = engine.memory_usage();

        Ok(Metrics {
            parse_time_ms: parse_time.as_secs_f64() * 1000.0,
            layout_time_ms: layout_time.as_secs_f64() * 1000.0,
            paint_time_ms: paint_time.as_secs_f64() * 1000.0,
            total_time_ms: total_time.as_secs_f64() * 1000.0,
            memory_mb: memory_used as f64 / 1_048_576.0,
        })
    }
}

/// Test results containing all metrics and statistics
#[derive(Debug, Serialize, Deserialize)]
pub struct TestResults {
    pub platform: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub git_commit: String,
    pub iterations: usize,
    pub total_duration_secs: f64,
    pub renderers: HashMap<String, Statistics>,
    pub regressions: Vec<Regression>,
    pub baseline_comparison: Option<BaselineComparison>,
}

impl TestResults {
    /// Save results to JSON file
    pub fn save(&self, path: &PathBuf) -> Result<()> {
        let json = serde_json::to_string_pretty(self)?;
        fs::write(path, json)?;
        Ok(())
    }

    /// Load results from JSON file
    pub fn load(path: &PathBuf) -> Result<Self> {
        let json = fs::read_to_string(path)?;
        let results = serde_json::from_str(&json)?;
        Ok(results)
    }

    /// Compare with baseline and detect regressions
    pub fn compare_with_baseline(&mut self, baseline_path: &PathBuf) -> Result<BaselineComparison> {
        let baseline = Self::load(baseline_path)?;
        
        let mut comparison = BaselineComparison {
            baseline_commit: baseline.git_commit.clone(),
            baseline_timestamp: baseline.timestamp,
            improvements: Vec::new(),
            regressions: Vec::new(),
        };

        // Compare each renderer
        for (renderer, current_stats) in &self.renderers {
            if let Some(baseline_stats) = baseline.renderers.get(renderer) {
                // Check total render time
                let current = current_stats.total_time.mean;
                let base = baseline_stats.total_time.mean;
                let change_pct = ((current - base) / base) * 100.0;

                if change_pct > 5.0 {
                    // Regression threshold: 5% slower
                    let regression = Regression {
                        renderer: renderer.clone(),
                        metric: "total_time_ms".to_string(),
                        baseline_value: base,
                        current_value: current,
                        percent_change: change_pct,
                    };
                    comparison.regressions.push(regression.clone());
                    self.regressions.push(regression);
                }

                // Check memory usage
                let current_mem = current_stats.memory.mean;
                let base_mem = baseline_stats.memory.mean;
                let mem_change_pct = ((current_mem - base_mem) / base_mem) * 100.0;

                if mem_change_pct > 15.0 {
                    // Memory regression threshold: 15% increase
                    let regression = Regression {
                        renderer: renderer.clone(),
                        metric: "memory_mb".to_string(),
                        baseline_value: base_mem,
                        current_value: current_mem,
                        percent_change: mem_change_pct,
                    };
                    comparison.regressions.push(regression.clone());
                    self.regressions.push(regression);
                }
            }
        }

        self.baseline_comparison = Some(comparison.clone());
        Ok(comparison)
    }

    /// Print summary to console
    pub fn print_summary(&self) {
        println!("\n{}", "=".repeat(80));
        println!("Performance Test Results");
        println!("{}", "=".repeat(80));
        println!("Platform: {}", self.platform);
        println!("Iterations: {}", self.iterations);
        println!("Duration: {:.2}s", self.total_duration_secs);
        println!("Git Commit: {}", self.git_commit);
        println!();

        for (renderer, stats) in &self.renderers {
            println!("Renderer: {}", renderer);
            println!("{}", "-".repeat(80));
            stats.print();
            println!();
        }

        if !self.regressions.is_empty() {
            println!("⚠️  REGRESSIONS DETECTED:");
            println!("{}", "-".repeat(80));
            for reg in &self.regressions {
                println!("  {} - {}: {:.2}% slower (baseline: {:.2}, current: {:.2})",
                         reg.renderer, reg.metric, reg.percent_change, 
                         reg.baseline_value, reg.current_value);
            }
            println!();
        }
    }
}

/// Get current platform
fn get_platform() -> String {
    if cfg!(target_os = "windows") {
        "windows".to_string()
    } else if cfg!(target_os = "macos") {
        "macos".to_string()
    } else if cfg!(target_os = "linux") {
        "linux".to_string()
    } else {
        "unknown".to_string()
    }
}

/// Get current git commit hash
fn get_git_commit() -> Result<String> {
    use std::process::Command;
    
    let output = Command::new("git")
        .args(["rev-parse", "--short", "HEAD"])
        .output()?;
    
    if output.status.success() {
        Ok(String::from_utf8(output.stdout)?.trim().to_string())
    } else {
        anyhow::bail!("Failed to get git commit")
    }
}
