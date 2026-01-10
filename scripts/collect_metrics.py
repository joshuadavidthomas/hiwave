#!/usr/bin/env python3
"""
collect_metrics.py - Aggregate metrics from platform submodules

Collects parity and performance metrics from each platform submodule
and aggregates them into metrics/unified.json for badge and chart generation.

Usage:
    python3 scripts/collect_metrics.py [--test]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import subprocess

REPO_ROOT = Path(__file__).parent.parent
METRICS_DIR = REPO_ROOT / "metrics"
UNIFIED_FILE = METRICS_DIR / "unified.json"

# Submodule paths
SUBMODULES = {
    "macos": REPO_ROOT / "hiwave-macos",
    "windows": REPO_ROOT / "hiwave-windows",
    "linux": REPO_ROOT / "hiwave-linux",
}

# Possible metric source files in each submodule
METRIC_SOURCES = [
    "parity-baseline/baseline_report.json",
    "progress_report.json",
    "parity_test_results.json",
]


def get_git_commit(submodule_path: Path) -> Optional[str]:
    """Get the current git commit hash for a submodule."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=submodule_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()[:7]
    except Exception:
        pass
    return None


def load_json_file(filepath: Path) -> Optional[Dict]:
    """Load a JSON file, returning None if it doesn't exist or fails."""
    if not filepath.exists():
        return None
    try:
        return json.loads(filepath.read_text())
    except Exception as e:
        print(f"  Warning: Could not parse {filepath}: {e}")
        return None


def extract_metrics_from_baseline(data: Dict) -> Dict[str, Any]:
    """Extract metrics from baseline_report.json format."""
    metrics = data.get("metrics", {})

    # Calculate parity as inverse of diff percentage
    tier_b_weighted_mean = metrics.get("tier_b_weighted_mean", 100)
    parity = max(0, 100 - tier_b_weighted_mean)

    # Get issue clusters
    issue_clusters = data.get("issue_clusters", {})

    # Get performance data (from first successful result if available)
    perf = {}
    for result in data.get("builtin_results", []) + data.get("websuite_results", []):
        result_perf = result.get("perf", {})
        if result_perf:
            perf = {
                "engine_init_ms": result_perf.get("engine_init_ms"),
                "html_load_ms": result_perf.get("html_load_ms"),
                "render_time_ms": result_perf.get("render_time_ms"),
            }
            break

    return {
        "parity": round(parity, 1),
        "tier_a_pass_rate": metrics.get("tier_a_pass_rate", 0),
        "tier_b_weighted_mean": tier_b_weighted_mean,
        "issue_clusters": issue_clusters,
        "perf": perf,
    }


def extract_metrics_from_progress(data: Dict) -> Dict[str, Any]:
    """Extract metrics from progress_report.json format."""
    return {
        "parity": data.get("parity", 0),
        "tier_a_pass_rate": data.get("tier_a_pass_rate", 0),
        "tier_b_weighted_mean": data.get("tier_b_weighted_mean", 100),
        "issue_clusters": data.get("issue_clusters", {}),
        "perf": data.get("perf", {}),
    }


def collect_platform_metrics(platform: str, submodule_path: Path) -> Optional[Dict[str, Any]]:
    """Collect metrics from a platform submodule."""
    if not submodule_path.exists():
        return None

    # Try to find metrics from various sources
    metrics_data = None
    source_file = None

    for source in METRIC_SOURCES:
        filepath = submodule_path / source
        data = load_json_file(filepath)
        if data:
            metrics_data = data
            source_file = source
            break

    if not metrics_data:
        print(f"  No metrics found for {platform}")
        return None

    print(f"  Found {source_file}")

    # Extract metrics based on file format
    if "baseline_report" in source_file:
        extracted = extract_metrics_from_baseline(metrics_data)
    else:
        extracted = extract_metrics_from_progress(metrics_data)

    # Add metadata
    extracted["last_updated"] = metrics_data.get("timestamp", datetime.now().isoformat())
    extracted["git_commit"] = get_git_commit(submodule_path)
    extracted["source_file"] = source_file

    return extracted


def calculate_perf_grade(perf: Dict) -> str:
    """Calculate overall performance grade A-F."""
    if not perf:
        return "?"

    # Scoring based on key metrics (lower is better for latency)
    score = 100

    engine_init = perf.get("engine_init_ms")
    if engine_init:
        if engine_init > 20:
            score -= 30
        elif engine_init > 10:
            score -= 15
        elif engine_init > 5:
            score -= 5

    render_time = perf.get("render_time_ms")
    if render_time:
        if render_time > 50:
            score -= 30
        elif render_time > 30:
            score -= 15
        elif render_time > 15:
            score -= 5

    # Convert score to grade
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def load_existing_unified() -> Dict[str, Any]:
    """Load existing unified metrics or create new structure."""
    if UNIFIED_FILE.exists():
        try:
            return json.loads(UNIFIED_FILE.read_text())
        except Exception:
            pass

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {},
        "history": []
    }


def update_history(unified: Dict, platforms: Dict) -> None:
    """Update historical data with today's metrics."""
    today = datetime.now().strftime("%Y-%m-%d")
    history = unified.get("history", [])

    # Check if we already have an entry for today
    today_entry = None
    for entry in history:
        if entry.get("date") == today:
            today_entry = entry
            break

    if not today_entry:
        today_entry = {"date": today}
        history.append(today_entry)

    # Update today's entry with platform parity values
    for platform, data in platforms.items():
        if data and "parity" in data:
            today_entry[platform] = data["parity"]

        # Also add performance data
        if data and data.get("perf"):
            if "perf" not in today_entry:
                today_entry["perf"] = {}
            for key, value in data["perf"].items():
                if value is not None:
                    today_entry["perf"][key] = value

    # Keep only last 90 days of history
    history = sorted(history, key=lambda x: x.get("date", ""))[-90:]
    unified["history"] = history


def generate_test_data() -> Dict[str, Any]:
    """Generate test data for testing the collector."""
    base_date = datetime.now()
    from datetime import timedelta

    history = []
    for i in range(30):
        date = base_date - timedelta(days=29-i)
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "macos": 85 + i * 0.4 + (i % 3) * 0.5,
            "windows": 75 + i * 0.5 + (i % 4) * 0.3,
            "linux": None if i < 20 else 70 + (i - 20) * 1.0,
            "perf": {
                "engine_init_ms": 6.0 - i * 0.05,
                "render_time_ms": 20.0 - i * 0.3,
            }
        })

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {
            "macos": {
                "parity": 98.7,
                "tier_a_pass_rate": 1.0,
                "tier_b_weighted_mean": 1.3,
                "issue_clusters": {"sizing_layout": 2, "paint": 0, "text": 1},
                "perf": {"engine_init_ms": 4.5, "render_time_ms": 12.3},
                "perf_grade": "A",
                "last_updated": datetime.now().isoformat(),
                "git_commit": "abc1234",
            },
            "windows": {
                "parity": 85.2,
                "tier_a_pass_rate": 0.85,
                "tier_b_weighted_mean": 14.8,
                "issue_clusters": {"sizing_layout": 5, "paint": 2, "text": 3},
                "perf": {"engine_init_ms": 5.2, "render_time_ms": 15.8},
                "perf_grade": "B",
                "last_updated": datetime.now().isoformat(),
                "git_commit": "def5678",
            },
            "linux": None
        },
        "history": history,
        "overall": {
            "parity": 85.2,
            "perf_grade": "B"
        }
    }


def main():
    test_mode = "--test" in sys.argv

    print("=" * 50)
    print("HiWave Metrics Collector")
    print("=" * 50)

    if test_mode:
        print("\nRunning in TEST mode with sample data")
        unified = generate_test_data()
    else:
        # Load existing data (to preserve history)
        unified = load_existing_unified()

        # Collect metrics from each platform
        print("\nCollecting platform metrics...")
        platforms = {}

        for platform, path in SUBMODULES.items():
            print(f"\n{platform.upper()}:")
            if path.exists():
                metrics = collect_platform_metrics(platform, path)
                if metrics:
                    # Add performance grade
                    metrics["perf_grade"] = calculate_perf_grade(metrics.get("perf", {}))
                platforms[platform] = metrics
            else:
                print(f"  Submodule not found: {path}")
                platforms[platform] = None

        # Update unified structure
        unified["generated_at"] = datetime.now().isoformat()
        unified["platforms"] = platforms

        # Calculate overall metrics
        parity_values = [
            p["parity"] for p in platforms.values()
            if p and "parity" in p
        ]
        if parity_values:
            unified["overall"] = {
                "parity": round(min(parity_values), 1),  # Overall is minimum
                "perf_grade": calculate_perf_grade(
                    # Use best performing platform's metrics
                    max(
                        (p.get("perf", {}) for p in platforms.values() if p),
                        key=lambda x: -sum(v or 999 for v in x.values()) if x else 0,
                        default={}
                    )
                )
            }

        # Update history
        update_history(unified, platforms)

    # Save unified metrics
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_FILE.write_text(json.dumps(unified, indent=2))
    print(f"\nSaved to: {UNIFIED_FILE}")

    # Print summary
    print("\n" + "=" * 50)
    print("Platform Summary:")
    print("=" * 50)

    for platform in ["macos", "windows", "linux"]:
        data = unified.get("platforms", {}).get(platform)
        if data:
            parity = data.get("parity", "?")
            tier_a = data.get("tier_a_pass_rate", 0)
            grade = data.get("perf_grade", "?")
            print(f"  {platform:8s}: {parity:>5.1f}% parity | Tier A: {tier_a*100:>5.1f}% | Perf: {grade}")
        else:
            print(f"  {platform:8s}: not available")

    overall = unified.get("overall", {})
    if overall:
        print(f"\n  Overall:  {overall.get('parity', '?')}% parity | Perf: {overall.get('perf_grade', '?')}")

    print(f"\nHistory: {len(unified.get('history', []))} days tracked")


if __name__ == "__main__":
    main()
