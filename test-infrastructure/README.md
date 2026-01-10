# HiWave Performance Testing Infrastructure

Automated Monte Carlo-style performance testing for the HiWave browser across all platforms.

## Architecture

```
test-infrastructure/
├── harness/              # Rust test harness binary
│   ├── src/
│   │   ├── main.rs       # CLI entry point
│   │   ├── test_suite.rs # Monte Carlo test runner
│   │   ├── metrics.rs    # Performance metrics collection
│   │   ├── renderers.rs  # Render engine abstractions
│   │   └── statistics.rs # Statistical analysis
│   └── Cargo.toml
├── pages/                # Test pages
│   ├── generate_test_pages.py    # Synthetic page generator
│   ├── download_real_pages.py    # Real-world page downloader
│   └── manifest.json              # Test page catalog
├── scripts/              # Analysis scripts
│   ├── regression-check.py       # Detect performance regressions
│   └── generate-report.py        # Create markdown reports
└── docker/               # Docker Compose setup (optional)
```

## Quick Start

### 1. Generate Test Pages

```bash
cd test-infrastructure/pages
python generate_test_pages.py
```

This creates 10+ synthetic HTML pages with varying complexity levels.

### 2. Run Local Performance Test

```bash
cd test-infrastructure/harness
cargo build --release
./target/release/hiwave-perf --iterations 100 --output test-results.json
```

### 3. Check for Regressions

```bash
cd test-infrastructure/scripts
python regression-check.py ../harness/test-results.json --baseline ../../hiwave-windows/perf_baseline.json
```

## GitHub Actions Integration

The workflow runs automatically:
- **Daily at 2 AM UTC** - Nightly performance checks
- **On workflow_dispatch** - Manual trigger with custom iterations

### Triggering Manually

1. Go to Actions tab in GitHub
2. Select "Performance Regression Testing"
3. Click "Run workflow"
4. Set iterations (default: 1000)
5. Monitor progress

### Results

Results are stored as artifacts for 30 days:
- `perf-results-windows.json`
- `perf-results-macos.json`
- `perf-results-linux.json`
- `performance-report.md`

## Test Harness CLI

```
hiwave-perf [OPTIONS]

OPTIONS:
    -i, --iterations <N>     Number of Monte Carlo iterations [default: 1000]
    -o, --output <FILE>      Output JSON file [default: perf-results.json]
    -r, --renderer <NAME>    Renderer to test: rustkit, webkit, blink, gecko, all [default: all]
    -p, --pages-dir <DIR>    Test pages directory [default: ../pages]
    -b, --baseline <FILE>    Baseline file for regression detection
    -v, --verbose            Verbose logging
```

### Examples

```bash
# Quick test with 100 iterations
./hiwave-perf -i 100

# Test only RustKit renderer
./hiwave-perf -r rustkit

# Compare against baseline
./hiwave-perf -b ../../hiwave-windows/perf_baseline.json

# Full test suite
./hiwave-perf -i 10000 -o comprehensive-results.json
```

## Metrics Collected

For each test iteration, we measure:
- **Parse Time**: HTML parsing duration (ms)
- **Layout Time**: Layout calculation duration (ms)
- **Paint Time**: Rendering/painting duration (ms)
- **Total Time**: End-to-end render time (ms)
- **Memory Usage**: Peak memory consumption (MB)

Statistics computed:
- Mean, Median, Min, Max
- P95 and P99 latencies
- Standard deviation
- Coefficient of variation

## Regression Detection

Regressions are automatically detected when:
- **Total Time** increases >5%
- **Individual Phases** increase >10%
- **Memory Usage** increases >15%

Thresholds are configurable in `scripts/regression-check.py`.

## Test Page Complexity Levels

Generated test pages span multiple complexity dimensions:

| Name | DOM Depth | Elements | CSS Rules |
|------|-----------|----------|-----------|
| simple | 5 | 50 | 10 |
| medium | 10 | 200 | 50 |
| complex | 15 | 1000 | 200 |
| very-complex | 20 | 2000 | 500 |
| extreme | 30 | 5000 | 1000 |
| deep-shallow | 50 | 100 | 10 |
| shallow-wide | 5 | 10000 | 50 |
| css-heavy | 10 | 1000 | 2000 |

## Randomization Strategy

Each test iteration randomizes:
1. **Test Page** - Random selection from available pages
2. **Viewport Size** - Random from common device sizes:
   - 320x568 (iPhone SE)
   - 375x667 (iPhone 8)
   - 414x896 (iPhone 11 Pro Max)
   - 768x1024 (iPad Portrait)
   - 1024x768 (iPad Landscape)
   - 1280x720 (HD)
   - 1920x1080 (Full HD)
   - 2560x1440 (QHD)

## Setting Up Self-Hosted Runner (Windows)

```powershell
# Download and configure GitHub Actions runner
mkdir C:\actions-runner
cd C:\actions-runner

# Download from GitHub (get latest URL from repo Settings > Actions > Runners)
Invoke-WebRequest -Uri <RUNNER_URL> -OutFile actions-runner.zip
Expand-Archive -Path actions-runner.zip -DestinationPath .

# Configure
.\config.cmd --url https://github.com/YourUsername/hiwave --token <YOUR_TOKEN>

# Install as service
.\svc.cmd install
.\svc.cmd start
```

## Python Environment Setup

```bash
cd test-infrastructure
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Adding New Test Pages

### Manual Addition

1. Create HTML file in `test-infrastructure/pages/`
2. Update `manifest.json`:

```json
{
  "pages": [
    {
      "file": "my-test-page.html",
      "name": "My Test Page",
      "complexity": {
        "dom_depth": 15,
        "element_count": 500,
        "css_rules": 100
      }
    }
  ]
}
```

### Real-World Pages

```bash
cd test-infrastructure/pages
python download_real_pages.py
```

This downloads and sanitizes real websites for offline testing.

## Baseline Updates

When you make intentional performance improvements:

```bash
# Run performance test
cd test-infrastructure/harness
./target/release/hiwave-perf -i 5000 -o new-baseline.json

# Update baseline
cp new-baseline.json ../../hiwave-windows/perf_baseline.json
git add ../../hiwave-windows/perf_baseline.json
git commit -m "Update performance baseline - 15% faster layout"
```

## Troubleshooting

### "No test pages found"

```bash
cd test-infrastructure/pages
python generate_test_pages.py
```

### "Baseline not found"

Either:
1. Create initial baseline: `./hiwave-perf -o baseline.json`
2. Skip baseline comparison: remove `--baseline` flag

### GitHub Actions runner offline

On Windows self-hosted runner:

```powershell
cd C:\actions-runner
.\svc.cmd status
.\svc.cmd start
```

### Python dependencies missing

```bash
cd test-infrastructure
pip install -r requirements.txt
```

## Performance Optimization Workflow

1. **Identify bottleneck** - Review regression reports
2. **Create hypothesis** - What's causing the slowdown?
3. **Implement fix** - Code changes in HiWave
4. **Local validation** - Run `hiwave-perf -i 100`
5. **Full test** - Run `hiwave-perf -i 10000`
6. **Update baseline** - If improvement verified
7. **Commit changes** - Include both code and baseline

## CI/CD Integration Best Practices

- **PR Checks**: Run 100-iteration quick test (~2 min)
- **Nightly Builds**: Full 1000+ iteration test
- **Release Validation**: 10,000+ iteration comprehensive test
- **Fail Fast**: Exit on first regression >10%
- **Trend Tracking**: Store results as artifacts for historical analysis

## Future Enhancements

- [ ] Grafana dashboard for trend visualization
- [ ] TimescaleDB integration for historical data
- [ ] Baseline renderer integration (WebKit, Blink, Gecko)
- [ ] GPU performance metrics
- [ ] Frame rate / animation smoothness testing
- [ ] Memory leak detection
- [ ] Network performance simulation

## Contributing

When adding new tests:
1. Add test pages to `pages/` directory
2. Update `manifest.json`
3. Ensure tests are deterministic (use fixed seeds for randomization)
4. Document expected performance characteristics
5. Update baselines after verification

## License

Same as HiWave main project.
