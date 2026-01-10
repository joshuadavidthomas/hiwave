# HiWave Performance Testing - Setup Guide

Complete guide for setting up automated performance testing across all platforms.

## Prerequisites

### All Platforms
- Rust 1.70+ (`rustup`)
- Python 3.11+
- Git

### Windows Specific
- PowerShell 5.1+
- Docker Desktop (optional, for local CI)
- Visual Studio Build Tools (for Rust)

### macOS Specific
- Xcode Command Line Tools
- Homebrew (recommended)

### Linux Specific
- build-essential
- pkg-config

## Installation Steps

### 1. Clone and Navigate

```bash
cd P:\petes_code\ClaudeCode\hiwave
```

### 2. Install Python Dependencies

```bash
cd test-infrastructure
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Generate Test Pages

```bash
cd pages
python generate_test_pages.py
```

Expected output:
```
Generating test-page-simple.html (depth=5, elements~50, css=10)...
Generating test-page-medium.html (depth=10, elements~200, css=50)...
...
✅ Generated 10 test pages
📄 Manifest written to manifest.json
```

### 4. Build Test Harness

```bash
cd ../harness
cargo build --release
```

This will take 5-10 minutes on first build.

### 5. Run Initial Test

```bash
# Quick validation test (100 iterations, ~1 minute)
./target/release/hiwave-perf -i 100 -o test-run.json -v

# Windows
.\target\release\hiwave-perf.exe -i 100 -o test-run.json -v
```

Expected output:
```
HiWave Performance Testing Harness
Iterations: 100
Output: test-run.json
Renderer: all
Loaded 10 test pages
Starting 100 iterations...
Progress: 100/100 iterations
Performance testing complete!
```

### 6. Verify Results

```bash
cd ../scripts
python regression-check.py ../harness/test-run.json
```

Should show:
```
⚠️  No baseline provided and no perf_baseline.json found
   Skipping regression detection (first run?)
```

This is normal for first run.

## GitHub Actions Setup (Windows Self-Hosted Runner)

### Step 1: Get Runner Token

1. Go to your HiWave repo on GitHub
2. Settings → Actions → Runners → New self-hosted runner
3. Select Windows
4. Copy the token shown

### Step 2: Install Runner

```powershell
# Create runner directory
mkdir C:\actions-runner
cd C:\actions-runner

# Download latest runner
# (Use URL from GitHub - example below)
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner.zip

# Extract
Expand-Archive -Path actions-runner.zip -DestinationPath .

# Configure (use token from Step 1)
.\config.cmd --url https://github.com/YOUR_USERNAME/hiwave --token YOUR_TOKEN_HERE

# When prompted:
# Enter name: "windows-hiwave-perf"
# Enter labels: "performance,windows"
# Accept defaults for everything else
```

### Step 3: Install as Service

```powershell
# Install Windows service
.\svc.cmd install

# Start service
.\svc.cmd start

# Verify
.\svc.cmd status
# Should show: "Running (Pid 1234)"
```

### Step 4: Verify in GitHub

1. Go to Settings → Actions → Runners
2. You should see "windows-hiwave-perf" with a green dot (Idle)

## macOS/Linux Self-Hosted Runners (Optional)

Only needed if you want additional test capacity beyond GitHub-hosted runners.

### macOS Setup

```bash
mkdir ~/actions-runner && cd ~/actions-runner

# Download (get URL from GitHub)
curl -o actions-runner-osx.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-x64-2.311.0.tar.gz
tar xzf actions-runner-osx.tar.gz

# Configure
./config.sh --url https://github.com/YOUR_USERNAME/hiwave --token YOUR_TOKEN

# Install as service
./svc.sh install
./svc.sh start
```

### Linux Setup

```bash
mkdir ~/actions-runner && cd ~/actions-runner

# Download
curl -o actions-runner-linux.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf actions-runner-linux.tar.gz

# Configure
./config.sh --url https://github.com/YOUR_USERNAME/hiwave --token YOUR_TOKEN

# Install as service (requires sudo)
sudo ./svc.sh install
sudo ./svc.sh start
```

## First GitHub Actions Run

### Manual Trigger

1. Go to Actions tab in GitHub repo
2. Select "Performance Regression Testing"
3. Click "Run workflow"
4. Set iterations: 100 (for first test)
5. Click green "Run workflow" button
6. Monitor progress (~5 minutes for 100 iterations)

### Verify Results

1. Click on the completed workflow run
2. Check job logs for each platform
3. Download artifacts:
   - `perf-results-windows.json`
   - `perf-results-macos.json`
   - `perf-results-linux.json`
   - `performance-report.md`
4. Open `performance-report.md` to see full analysis

## Establishing Baselines

After your first successful test run:

```bash
# On Windows
cd P:\petes_code\ClaudeCode\hiwave\test-infrastructure\harness
.\target\release\hiwave-perf.exe -i 5000 -o baseline-windows.json

# Copy to appropriate location
copy baseline-windows.json ..\..\hiwave-windows\perf_baseline.json
```

Do the same for macOS and Linux if running locally.

Commit the baselines:

```bash
git add hiwave-windows/perf_baseline.json
git add hiwave-macos/perf_baseline.json
git add hiwave-linux/perf_baseline.json
git commit -m "Add initial performance baselines"
git push
```

## Validation Checklist

- [ ] Python environment activated and dependencies installed
- [ ] Test pages generated (10 .html files in `pages/`)
- [ ] Test harness builds successfully
- [ ] Local test runs without errors
- [ ] GitHub Actions runner shows as "Idle" (Windows)
- [ ] First GitHub Actions workflow completes successfully
- [ ] Performance baselines established and committed

## Troubleshooting

### Rust Build Fails on Windows

```powershell
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Or download from:
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### Python Module Not Found

```bash
# Ensure venv is activated
# Windows
test-infrastructure\venv\Scripts\activate

# macOS/Linux
source test-infrastructure/venv/bin/activate

# Reinstall
pip install -r test-infrastructure/requirements.txt
```

### GitHub Runner Not Connecting

```powershell
# Check service status
cd C:\actions-runner
.\svc.cmd status

# If stopped, start it
.\svc.cmd start

# Check logs
Get-Content -Path "_diag\Runner_*.log" -Tail 50
```

### Test Harness Can't Find Pages

```bash
# Verify manifest exists
ls test-infrastructure/pages/manifest.json

# Regenerate if needed
cd test-infrastructure/pages
python generate_test_pages.py
```

## Next Steps

After setup is complete:

1. **Daily Monitoring** - Review nightly test results
2. **Baseline Updates** - Update baselines after verified improvements
3. **Trend Analysis** - Track performance over time using artifacts
4. **Optimization** - Use regression reports to guide performance work
5. **Documentation** - Document any platform-specific findings

## Support

For issues specific to:
- **Test Infrastructure**: See `test-infrastructure/README.md`
- **GitHub Actions**: Check workflow file `.github/workflows/performance-test.yml`
- **RustKit Integration**: See `hiwave-*/crates/rustkit-bench/`

## Maintenance

### Weekly
- Review nightly test results
- Clean up old artifacts (auto-deleted after 30 days)

### Monthly
- Update baselines if consistent improvements seen
- Review and adjust regression thresholds if needed
- Update Python dependencies: `pip install -U -r requirements.txt`

### Quarterly
- Review test page coverage
- Add new complexity scenarios if needed
- Evaluate baseline renderer integration progress
