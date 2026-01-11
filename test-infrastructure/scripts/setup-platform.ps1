# Setup RustKit dependencies for Windows platform

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HarnessDir = Join-Path $ScriptDir "..\harness"

Write-Host "Setting up RustKit dependencies for Windows..." -ForegroundColor Yellow

# Check if hiwave-windows directory exists
$HiwaveDir = Join-Path $ScriptDir "..\..\..\hiwave-windows"

if (-not (Test-Path $HiwaveDir)) {
    Write-Host "ERROR: $HiwaveDir does not exist" -ForegroundColor Red
    Write-Host ""
    Write-Host "This script expects the following directory structure:"
    Write-Host "  hiwave/"
    Write-Host "  hiwave-windows/"
    Write-Host ""
    Write-Host "The test harness needs access to RustKit crates in hiwave-windows/"
    exit 1
}

# Update Cargo.toml
$CargoToml = @"
[package]
name = "hiwave-test-harness"
version = "0.1.0"
edition = "2021"
authors = ["HiWave Team"]

[[bin]]
name = "hiwave-perf"
path = "src/main.rs"

[dependencies]
# Core dependencies
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
anyhow = "1.0"
thiserror = "2.0"

# CLI
clap = { version = "4.5", features = ["derive"] }

# Randomization for Monte Carlo
rand = "0.8"

# Logging
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# Time
chrono = { version = "0.4", features = ["serde"] }

# RustKit dependencies - pointing to hiwave-windows
rustkit-dom = { path = "../../../hiwave-windows/crates/rustkit-dom" }
rustkit-css = { path = "../../../hiwave-windows/crates/rustkit-css" }
rustkit-layout = { path = "../../../hiwave-windows/crates/rustkit-layout" }

[dev-dependencies]
tempfile = "3.8"
"@

Set-Content -Path "$HarnessDir\Cargo.toml" -Value $CargoToml

Write-Host "✅ Cargo.toml updated for Windows" -ForegroundColor Green
Write-Host ""
Write-Host "RustKit crate paths:"
Write-Host "  - rustkit-dom: $HiwaveDir\crates\rustkit-dom"
Write-Host "  - rustkit-css: $HiwaveDir\crates\rustkit-css"
Write-Host "  - rustkit-layout: $HiwaveDir\crates\rustkit-layout"
