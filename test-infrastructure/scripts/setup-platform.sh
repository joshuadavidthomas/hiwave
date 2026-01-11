#!/bin/bash
# Setup RustKit dependencies for the current platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$SCRIPT_DIR/../harness"

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
else
    echo "Unknown platform: $OSTYPE"
    exit 1
fi

echo "Setting up RustKit dependencies for platform: $PLATFORM"

# Check if platform-specific hiwave directory exists
HIWAVE_DIR="$SCRIPT_DIR/../../../hiwave-$PLATFORM"

if [ ! -d "$HIWAVE_DIR" ]; then
    echo "ERROR: $HIWAVE_DIR does not exist"
    echo ""
    echo "This script expects the following directory structure:"
    echo "  hiwave/"
    echo "  hiwave-windows/"
    echo "  hiwave-macos/"
    echo "  hiwave-linux/"
    echo ""
    echo "For CI/CD, you need to either:"
    echo "1. Clone all three platform repos in the same parent directory, OR"
    echo "2. Use a monorepo structure with all platforms"
    exit 1
fi

# Update Cargo.toml to point to the correct platform
cd "$HARNESS_DIR"

echo "Updating Cargo.toml to use hiwave-$PLATFORM paths..."

# Create a temporary Cargo.toml with correct paths
cat > Cargo.toml << EOF
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

# RustKit dependencies - pointing to hiwave-$PLATFORM
rustkit-dom = { path = "../../../hiwave-$PLATFORM/crates/rustkit-dom" }
rustkit-css = { path = "../../../hiwave-$PLATFORM/crates/rustkit-css" }
rustkit-layout = { path = "../../../hiwave-$PLATFORM/crates/rustkit-layout" }

[dev-dependencies]
tempfile = "3.8"
EOF

echo "✅ Cargo.toml updated for $PLATFORM"
echo ""
echo "RustKit crate paths:"
echo "  - rustkit-dom: $HIWAVE_DIR/crates/rustkit-dom"
echo "  - rustkit-css: $HIWAVE_DIR/crates/rustkit-css"
echo "  - rustkit-layout: $HIWAVE_DIR/crates/rustkit-layout"
