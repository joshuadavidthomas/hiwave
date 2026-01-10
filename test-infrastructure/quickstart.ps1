# HiWave Performance Testing - Quick Start
# Run this script to set up and test the performance infrastructure

Write-Host "🚀 HiWave Performance Testing Setup" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Rust
try {
    $rustVersion = rustc --version 2>&1
    Write-Host "✅ Rust: $rustVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Rust not found. Please install from https://rustup.rs" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

Write-Host "`nAll prerequisites met!`n" -ForegroundColor Green

# Step 1: Python virtual environment
Write-Host "Step 1: Setting up Python environment..." -ForegroundColor Yellow

cd test-infrastructure

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

Write-Host "Activating virtual environment..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Gray
pip install -q -r requirements.txt
Write-Host "✅ Python dependencies installed`n" -ForegroundColor Green

# Step 2: Generate test pages
Write-Host "Step 2: Generating test pages..." -ForegroundColor Yellow

cd pages
python generate_test_pages.py

if (Test-Path "manifest.json") {
    $manifest = Get-Content manifest.json | ConvertFrom-Json
    $pageCount = $manifest.pages.Count
    Write-Host "✅ Generated $pageCount test pages`n" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to generate test pages" -ForegroundColor Red
    exit 1
}

cd ..

# Step 3: Build test harness
Write-Host "Step 3: Building test harness (this may take 5-10 minutes)..." -ForegroundColor Yellow

cd harness

if (-not (Test-Path "target/release/hiwave-perf.exe")) {
    Write-Host "Building in release mode..." -ForegroundColor Gray
    cargo build --release
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test harness built successfully`n" -ForegroundColor Green
    } else {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Test harness already built`n" -ForegroundColor Green
}

# Step 4: Run quick validation test
Write-Host "Step 4: Running validation test (100 iterations)..." -ForegroundColor Yellow

.\target\release\hiwave-perf.exe -i 100 -o validation-test.json -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Validation test completed`n" -ForegroundColor Green
} else {
    Write-Host "❌ Test failed" -ForegroundColor Red
    exit 1
}

# Step 5: Verify results
Write-Host "Step 5: Verifying results..." -ForegroundColor Yellow

cd ../scripts

if (Test-Path "../harness/validation-test.json") {
    $results = Get-Content ../harness/validation-test.json | ConvertFrom-Json
    Write-Host "✅ Results file created" -ForegroundColor Green
    Write-Host "   Platform: $($results.platform)" -ForegroundColor Gray
    Write-Host "   Iterations: $($results.iterations)" -ForegroundColor Gray
    Write-Host "   Commit: $($results.git_commit)" -ForegroundColor Gray
} else {
    Write-Host "❌ Results file not found" -ForegroundColor Red
    exit 1
}

cd ../..

# Summary
Write-Host "`n" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: test-infrastructure/SETUP.md" -ForegroundColor White
Write-Host "  2. Set up GitHub Actions runner (optional)" -ForegroundColor White
Write-Host "  3. Integrate with RustKit (see IMPLEMENTATION_SUMMARY.md)" -ForegroundColor White
Write-Host ""
Write-Host "To run tests manually:" -ForegroundColor Yellow
Write-Host "  cd test-infrastructure/harness" -ForegroundColor White
Write-Host "  .\target\release\hiwave-perf.exe -i 1000" -ForegroundColor White
Write-Host ""
Write-Host "To check for regressions:" -ForegroundColor Yellow
Write-Host "  cd test-infrastructure/scripts" -ForegroundColor White
Write-Host "  python regression-check.py ../harness/perf-results.json" -ForegroundColor White
Write-Host ""
