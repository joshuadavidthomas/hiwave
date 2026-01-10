#!/usr/bin/env python3
"""
generate_charts.py - Generate SVG charts for HiWave cross-platform metrics

Generates trend charts from metrics/unified.json:
- Parity trend (multi-line, all platforms over time)
- Platform comparison (bar chart, latest values)
- Performance trend (multi-line, key metrics over time)

Usage:
    python3 scripts/generate_charts.py [--test]

Requires: pygal, lxml
    pip install pygal lxml
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).parent.parent
METRICS_FILE = REPO_ROOT / "metrics" / "unified.json"
CHARTS_DIR = REPO_ROOT / "charts"

# Try to import pygal, provide fallback if not available
try:
    import pygal
    from pygal.style import Style
    PYGAL_AVAILABLE = True
except ImportError:
    PYGAL_AVAILABLE = False
    print("Warning: pygal not installed. Using basic SVG fallback.")
    print("Install with: pip install pygal lxml")

# Custom style for HiWave charts
HIWAVE_STYLE = None
if PYGAL_AVAILABLE:
    HIWAVE_STYLE = Style(
        background='transparent',
        plot_background='transparent',
        foreground='#333',
        foreground_strong='#333',
        foreground_subtle='#666',
        opacity='.8',
        opacity_hover='.9',
        transition='400ms',
        colors=('#4c1', '#007ec6', '#fe7d37', '#e05d44', '#9f9f9f')
    )


def load_metrics() -> Dict[str, Any]:
    """Load metrics from unified.json."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")
    return {"platforms": {}, "history": []}


def generate_test_data() -> Dict[str, Any]:
    """Generate test data for chart testing."""
    base_date = datetime.now()
    history = []

    # Generate 30 days of fake history
    for i in range(30):
        date = base_date - timedelta(days=29-i)
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "macos": 85 + i * 0.4 + (i % 3) * 0.5,  # Trending up with noise
            "windows": 75 + i * 0.5 + (i % 4) * 0.3,  # Also trending up
            "linux": None if i < 20 else 70 + (i - 20) * 1.0,  # Starts later
            "perf": {
                "engine_init_ms": 6.0 - i * 0.05,  # Getting faster
                "render_time_ms": 20.0 - i * 0.3,
            }
        })

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {
            "macos": {"parity": 98.7, "tier_a_pass_rate": 1.0},
            "windows": {"parity": 89.5, "tier_a_pass_rate": 0.85},
            "linux": {"parity": 80.0, "tier_a_pass_rate": 0.7},
        },
        "history": history
    }


def generate_parity_trend_pygal(history: List[Dict]) -> str:
    """Generate parity trend chart using pygal."""
    chart = pygal.Line(
        width=800,
        height=300,
        style=HIWAVE_STYLE,
        show_legend=True,
        legend_at_bottom=True,
        x_label_rotation=45,
        show_minor_x_labels=False,
        truncate_label=10,
        dots_size=2,
        stroke_style={'width': 2},
        title="Parity Trend (Last 30 Days)"
    )

    # Extract dates for x-axis (show every 5th label)
    dates = [h.get("date", "")[-5:] for h in history]  # MM-DD format
    chart.x_labels = dates
    chart.x_labels_major = dates[::5]  # Show every 5th label

    # Extract parity values per platform
    macos_values = [h.get("macos") for h in history]
    windows_values = [h.get("windows") for h in history]
    linux_values = [h.get("linux") for h in history]

    chart.add("macOS", macos_values)
    chart.add("Windows", windows_values)
    chart.add("Linux", linux_values)

    return chart.render(is_unicode=True)


def generate_platform_comparison_pygal(platforms: Dict) -> str:
    """Generate platform comparison bar chart using pygal."""
    chart = pygal.Bar(
        width=600,
        height=300,
        style=HIWAVE_STYLE,
        show_legend=False,
        title="Platform Parity Comparison",
        y_title="Parity %",
        range=(0, 100)
    )

    chart.x_labels = ["macOS", "Windows", "Linux"]

    values = [
        (platforms.get("macos") or {}).get("parity"),
        (platforms.get("windows") or {}).get("parity"),
        (platforms.get("linux") or {}).get("parity"),
    ]

    chart.add("Parity", values)

    return chart.render(is_unicode=True)


def generate_perf_trend_pygal(history: List[Dict]) -> str:
    """Generate performance trend chart using pygal."""
    chart = pygal.Line(
        width=800,
        height=300,
        style=HIWAVE_STYLE,
        show_legend=True,
        legend_at_bottom=True,
        x_label_rotation=45,
        show_minor_x_labels=False,
        truncate_label=10,
        dots_size=2,
        title="Performance Trend (ms)"
    )

    dates = [h.get("date", "")[-5:] for h in history]
    chart.x_labels = dates
    chart.x_labels_major = dates[::5]

    # Extract performance values
    engine_init = []
    render_time = []

    for h in history:
        perf = h.get("perf", {})
        engine_init.append(perf.get("engine_init_ms"))
        render_time.append(perf.get("render_time_ms"))

    chart.add("Engine Init", engine_init)
    chart.add("Render Time", render_time)

    return chart.render(is_unicode=True)


def generate_basic_svg_chart(title: str, message: str) -> str:
    """Generate a basic SVG placeholder when pygal isn't available."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="200" viewBox="0 0 600 200">
  <rect width="100%" height="100%" fill="#f5f5f5" rx="5"/>
  <text x="300" y="80" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#333">{title}</text>
  <text x="300" y="120" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">{message}</text>
  <text x="300" y="150" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#999">Install pygal for full charts: pip install pygal lxml</text>
</svg>'''


def generate_all_charts(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Generate all charts from metrics."""
    charts = {}
    history = metrics.get("history", [])
    platforms = metrics.get("platforms", {})

    if PYGAL_AVAILABLE and history:
        # Use pygal for full chart generation
        charts["parity-trend.svg"] = generate_parity_trend_pygal(history[-30:])
        charts["platform-comparison.svg"] = generate_platform_comparison_pygal(platforms)
        charts["perf-trend.svg"] = generate_perf_trend_pygal(history[-30:])
    else:
        # Fallback to basic SVG placeholders
        if not PYGAL_AVAILABLE:
            msg = "pygal not installed"
        else:
            msg = "No historical data available"

        charts["parity-trend.svg"] = generate_basic_svg_chart("Parity Trend", msg)
        charts["platform-comparison.svg"] = generate_basic_svg_chart("Platform Comparison", msg)
        charts["perf-trend.svg"] = generate_basic_svg_chart("Performance Trend", msg)

    return charts


def save_charts(charts: Dict[str, str]) -> None:
    """Save all charts to the charts directory."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in charts.items():
        filepath = CHARTS_DIR / filename
        filepath.write_text(content)
        print(f"  Generated: {filename}")


def main():
    test_mode = "--test" in sys.argv

    print("=" * 50)
    print("HiWave Chart Generator")
    print("=" * 50)

    if PYGAL_AVAILABLE:
        print("Using pygal for chart generation")
    else:
        print("WARNING: pygal not available, using basic fallback")

    # Load or generate metrics
    print("\nLoading metrics...")
    if test_mode:
        print("Running in TEST mode with sample data")
        metrics = generate_test_data()
    else:
        metrics = load_metrics()

    history_count = len(metrics.get("history", []))
    print(f"  Found {history_count} historical data points")

    # Generate charts
    print("\nGenerating charts...")
    charts = generate_all_charts(metrics)

    # Save charts
    print(f"\nSaving to {CHARTS_DIR}/")
    save_charts(charts)

    print(f"\nGenerated {len(charts)} charts successfully!")


if __name__ == "__main__":
    main()
