use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;
use tracing::{info, warn};
use tracing_subscriber::EnvFilter;

mod metrics;
mod renderers;
mod statistics;
mod test_suite;

use crate::test_suite::MonteCarloTest;

#[derive(Parser, Debug)]
#[command(name = "hiwave-perf")]
#[command(about = "HiWave Performance Testing Harness", long_about = None)]
struct Args {
    /// Number of Monte Carlo iterations
    #[arg(short, long, default_value_t = 1000)]
    iterations: usize,

    /// Output JSON file path
    #[arg(short, long, default_value = "perf-results.json")]
    output: PathBuf,

    /// Renderer to test (rustkit, webkit, blink, gecko, all)
    #[arg(short, long, default_value = "all")]
    renderer: String,

    /// Test pages directory
    #[arg(short = 'p', long, default_value = "../pages")]
    pages_dir: PathBuf,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,

    /// Baseline comparison file (optional)
    #[arg(short, long)]
    baseline: Option<PathBuf>,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize logging
    let filter = if args.verbose {
        EnvFilter::new("debug")
    } else {
        EnvFilter::new("info")
    };

    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .init();

    info!("HiWave Performance Testing Harness");
    info!("Iterations: {}", args.iterations);
    info!("Output: {}", args.output.display());
    info!("Renderer: {}", args.renderer);

    // Create test suite
    let mut test = MonteCarloTest::new(args.iterations, args.pages_dir.clone())?;

    // Configure renderers based on CLI args
    match args.renderer.to_lowercase().as_str() {
        "rustkit" => test.enable_renderer("rustkit"),
        "webkit" => test.enable_renderer("webkit"),
        "blink" => test.enable_renderer("blink"),
        "gecko" => test.enable_renderer("gecko"),
        "all" => {
            test.enable_renderer("rustkit");
            // Note: Baseline renderers may not be available on all platforms
            if cfg!(target_os = "macos") {
                test.enable_renderer("webkit");
            }
            // Add other baseline renderers as they become available
        }
        other => {
            warn!("Unknown renderer '{}', defaulting to rustkit only", other);
            test.enable_renderer("rustkit");
        }
    }

    // Run tests
    info!("Running Monte Carlo performance tests...");
    let mut results = test.run()?;

    // Compare against baseline if provided
    if let Some(baseline_path) = args.baseline {
        info!("Comparing against baseline: {}", baseline_path.display());
        match results.compare_with_baseline(&baseline_path) {
            Ok(comparison) => {
                info!("Baseline comparison complete");
                if !comparison.regressions.is_empty() {
                    warn!("⚠️  {} regression(s) detected!", comparison.regressions.len());
                    for reg in &comparison.regressions {
                        warn!("  - {}: {:.2}% slower", reg.metric, reg.percent_change);
                    }
                } else {
                    info!("✅ No regressions detected");
                }
            }
            Err(e) => {
                warn!("Failed to compare with baseline: {}", e);
            }
        }
    }

    // Save results
    info!("Saving results to {}", args.output.display());
    results.save(&args.output)?;

    // Print summary
    results.print_summary();

    info!("Performance testing complete!");

    Ok(())
}
