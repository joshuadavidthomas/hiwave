#!/usr/bin/env python3
"""
aggregate_parity_results.py - Aggregate parity results from all platforms

Reads swarm_report.json from each platform's results and produces unified
metrics/parity_results.json for badge and chart generation.

Usage:
    python scripts/aggregate_parity_results.py --input-dir all-results --output metrics/parity_results.json
    python scripts/aggregate_parity_results.py --input-dir artifacts --output metrics/parity_results.json --verbose
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()


def find_swarm_reports(input_dir: Path) -> Dict[str, List[Path]]:
    """Find all swarm_report.json grouped by platform."""
    platforms = {"macos": [], "windows": [], "linux": []}

    for path in input_dir.rglob("swarm_report.json"):
        path_str = str(path).lower()
        for platform in platforms:
            if platform in path_str:
                platforms[platform].append(path)
                break

    return platforms


def load_report(path: Path) -> Optional[Dict]:
    """Load a JSON report file."""
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Failed to load {path}: {e}")
        return None


def extract_metrics(reports: List[Path]) -> Optional[Dict[str, Any]]:
    """Extract aggregated metrics from swarm reports for a platform."""
    all_results = []

    for report_path in reports:
        report = load_report(report_path)
        if not report:
            continue
        all_results.extend(report.get("results", []))

    if not all_results:
        return None

    # Calculate metrics
    diffs = [r.get("diff_pct_median", 100) for r in all_results if r.get("diff_pct_median") is not None]
    passed = sum(1 for r in all_results if r.get("passed", False))
    stable = sum(1 for r in all_results if r.get("stable", False))
    errors = sum(1 for r in all_results if r.get("error") is not None)

    if not diffs:
        return None

    avg_diff = sum(diffs) / len(diffs)
    visual_parity = 100 - avg_diff

    return {
        "visual_parity": round(visual_parity, 2),
        "avg_diff_pct": round(avg_diff, 2),
        "tests_passed": passed,
        "tests_failed": len(all_results) - passed,
        "tests_total": len(all_results),
        "tests_stable": stable,
        "tests_errors": errors,
        "pass_rate": round(passed / len(all_results) * 100, 1) if all_results else 0,
        "results": all_results,
    }


def aggregate_all_platforms(
    input_dir: Path,
    output_path: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Aggregate parity results from all platforms."""
    print("=" * 60)
    print("Cross-Platform Parity Results Aggregation")
    print("=" * 60)
    print(f"Input: {input_dir}")
    print(f"Output: {output_path}")
    print()

    # Find reports by platform
    platform_reports = find_swarm_reports(input_dir)

    print("Found reports:")
    for platform, paths in platform_reports.items():
        print(f"  {platform}: {len(paths)} report(s)")
        if verbose:
            for p in paths:
                print(f"    - {p}")

    print()

    # Extract metrics for each platform
    platform_metrics = {}
    for platform, paths in platform_reports.items():
        if paths:
            metrics = extract_metrics(paths)
            if metrics:
                platform_metrics[platform] = metrics
                print(f"{platform.capitalize()}:")
                print(f"  Visual Parity: {metrics['visual_parity']:.1f}%")
                print(f"  Pass Rate: {metrics['pass_rate']:.1f}%")
                print(f"  Tests: {metrics['tests_passed']}/{metrics['tests_total']}")
            else:
                print(f"{platform.capitalize()}: No valid results")
        else:
            print(f"{platform.capitalize()}: No reports found")

    print()

    # Calculate overall metrics (average across platforms with data)
    platforms_with_data = [m for m in platform_metrics.values() if m]

    if not platforms_with_data:
        print("No valid results from any platform!")
        return {"error": "No valid results"}

    overall_parity = sum(m["visual_parity"] for m in platforms_with_data) / len(platforms_with_data)
    overall_pass_rate = sum(m["pass_rate"] for m in platforms_with_data) / len(platforms_with_data)
    total_tests = sum(m["tests_total"] for m in platforms_with_data)
    total_passed = sum(m["tests_passed"] for m in platforms_with_data)

    # Build unified report
    unified_report = {
        "timestamp": datetime.now().isoformat(),
        "input_dir": str(input_dir),
        "platforms_found": list(platform_metrics.keys()),
        "overall": {
            "visual_parity": round(overall_parity, 2),
            "pass_rate": round(overall_pass_rate, 1),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "platform_count": len(platforms_with_data),
        },
        "by_platform": {
            platform: {
                "visual_parity": metrics["visual_parity"],
                "avg_diff_pct": metrics["avg_diff_pct"],
                "pass_rate": metrics["pass_rate"],
                "tests_passed": metrics["tests_passed"],
                "tests_failed": metrics["tests_failed"],
                "tests_total": metrics["tests_total"],
                "tests_stable": metrics["tests_stable"],
            }
            for platform, metrics in platform_metrics.items()
        },
        # Include detailed results for each platform
        "detailed_results": {
            platform: metrics.get("results", [])
            for platform, metrics in platform_metrics.items()
        },
    }

    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(unified_report, f, indent=2, default=str)

    # Print summary
    print("=" * 60)
    print("Overall Summary")
    print("=" * 60)
    print(f"Visual Parity: {overall_parity:.1f}%")
    print(f"Pass Rate: {overall_pass_rate:.1f}%")
    print(f"Total Tests: {total_tests} ({total_passed} passed)")
    print(f"Platforms: {len(platforms_with_data)}")
    print()
    print(f"Report saved to: {output_path}")

    return unified_report


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate parity results from all platforms"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing platform artifacts with swarm_report.json files",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=REPO_ROOT / "metrics" / "parity_results.json",
        help="Output path for unified report",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    report = aggregate_all_platforms(
        input_dir=args.input_dir,
        output_path=args.output,
        verbose=args.verbose,
    )

    # Exit with error code if overall parity is below 50%
    overall_parity = report.get("overall", {}).get("visual_parity", 0)
    if overall_parity < 50:
        print(f"\nWarning: Overall parity ({overall_parity}%) is below 50%")
        sys.exit(1)


if __name__ == "__main__":
    main()
