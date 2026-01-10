#!/usr/bin/env python3
"""
Regression detection script for performance testing.
Compares current results against baseline and detects regressions.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class RegressionDetector:
    """Detect performance regressions by comparing metrics."""
    
    # Regression thresholds (percentage increase)
    THRESHOLDS = {
        'total_time_ms': 5.0,      # 5% slowdown is a regression
        'parse_time_ms': 10.0,     # 10% for individual phases
        'layout_time_ms': 10.0,
        'paint_time_ms': 10.0,
        'memory_mb': 15.0,         # 15% memory increase
    }
    
    def __init__(self, current_results: Dict, baseline_results: Dict):
        self.current = current_results
        self.baseline = baseline_results
        self.regressions = []
        self.improvements = []
    
    def compare_metric(self, renderer: str, metric_name: str, 
                      current_value: float, baseline_value: float) -> Tuple[str, float]:
        """Compare a single metric and classify as regression/improvement/neutral."""
        
        if baseline_value == 0:
            return 'neutral', 0.0
        
        percent_change = ((current_value - baseline_value) / baseline_value) * 100.0
        threshold = self.THRESHOLDS.get(metric_name, 5.0)
        
        if percent_change > threshold:
            return 'regression', percent_change
        elif percent_change < -threshold:
            return 'improvement', percent_change
        else:
            return 'neutral', percent_change
    
    def analyze(self) -> Dict:
        """Analyze all renderers and metrics for regressions."""
        
        # Check if baseline has the expected format
        if 'renderers' not in self.baseline:
            print("[WARN] Baseline file missing 'renderers' key - cannot compare")
            print("[INFO] Baseline may be in old format or empty")
            return {
                'regressions': [],
                'improvements': [],
                'baseline_commit': self.baseline.get('git_commit', 'unknown'),
                'baseline_timestamp': self.baseline.get('timestamp', 'unknown'),
                'error': 'Invalid baseline format'
            }
        
        if 'renderers' not in self.current:
            print("[WARN] Current results missing 'renderers' key - cannot compare")
            return {
                'regressions': [],
                'improvements': [],
                'baseline_commit': self.baseline.get('git_commit', 'unknown'),
                'baseline_timestamp': self.baseline.get('timestamp', 'unknown'),
                'error': 'Invalid current results format'
            }
        
        for renderer, current_stats in self.current['renderers'].items():
            if renderer not in self.baseline['renderers']:
                print(f"[WARN] Renderer '{renderer}' not found in baseline, skipping")
                continue
            
            baseline_stats = self.baseline['renderers'][renderer]
            
            # Compare each metric type
            for metric_type in ['parse_time', 'layout_time', 'paint_time', 'total_time', 'memory']:
                if metric_type not in current_stats or metric_type not in baseline_stats:
                    continue
                    
                current_mean = current_stats[metric_type]['mean']
                baseline_mean = baseline_stats[metric_type]['mean']
                
                metric_name = f"{metric_type.replace('_time', '_time_ms') if 'time' in metric_type else metric_type}"
                if metric_type == 'memory':
                    metric_name = 'memory_mb'
                
                classification, percent_change = self.compare_metric(
                    renderer, metric_name, current_mean, baseline_mean
                )
                
                result = {
                    'renderer': renderer,
                    'metric': metric_name,
                    'baseline_value': baseline_mean,
                    'current_value': current_mean,
                    'percent_change': percent_change,
                }
                
                if classification == 'regression':
                    self.regressions.append(result)
                elif classification == 'improvement':
                    self.improvements.append(result)
        
        return {
            'regressions': self.regressions,
            'improvements': self.improvements,
            'baseline_commit': self.baseline.get('git_commit', 'unknown'),
            'baseline_timestamp': self.baseline.get('timestamp', 'unknown'),
        }
    
    def print_report(self):
        """Print a human-readable regression report."""
        
        print("\n" + "=" * 80)
        print("PERFORMANCE REGRESSION ANALYSIS")
        print("=" * 80)
        print(f"Baseline: {self.baseline.get('git_commit', 'unknown')} @ {self.baseline.get('timestamp', 'unknown')[:10]}")
        print(f"Current:  {self.current.get('git_commit', 'unknown')} @ {self.current.get('timestamp', 'unknown')[:10]}")
        print()
        
        if self.regressions:
            print(f"[WARN] {len(self.regressions)} REGRESSION(S) DETECTED:")
            print("-" * 80)
            for reg in self.regressions:
                print(f"  {reg['renderer']:10} | {reg['metric']:20} | {reg['percent_change']:+6.2f}% "
                      f"(baseline: {reg['baseline_value']:7.2f}, current: {reg['current_value']:7.2f})")
            print()
        else:
            print("[OK] No regressions detected!")
            print()
        
        if self.improvements:
            print(f"[INFO] {len(self.improvements)} IMPROVEMENT(S):")
            print("-" * 80)
            for imp in self.improvements:
                print(f"  {imp['renderer']:10} | {imp['metric']:20} | {imp['percent_change']:+6.2f}% "
                      f"(baseline: {imp['baseline_value']:7.2f}, current: {imp['current_value']:7.2f})")
            print()


def main():
    parser = argparse.ArgumentParser(description='Detect performance regressions')
    parser.add_argument('results_file', type=Path, help='Current test results JSON')
    parser.add_argument('--baseline', type=Path, help='Baseline results JSON for comparison')
    parser.add_argument('--output', type=Path, help='Output regression report JSON')
    args = parser.parse_args()
    
    # Load current results
    try:
        with open(args.results_file) as f:
            current_results = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Results file not found: {args.results_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in results file: {args.results_file}")
        sys.exit(1)
    
    # If no baseline provided, try to find one
    if not args.baseline:
        # Look for perf_baseline.json in parent directories
        baseline_candidates = [
            args.results_file.parent / 'perf_baseline.json',
            args.results_file.parent.parent / 'perf_baseline.json',
            args.results_file.parent.parent.parent / 'perf_baseline.json',
        ]
        
        for candidate in baseline_candidates:
            if candidate.exists():
                args.baseline = candidate
                print(f"[INFO] Using baseline: {args.baseline}")
                break
    
    if not args.baseline or not args.baseline.exists():
        print("[WARN] No baseline provided or baseline file not found")
        print("[INFO] Skipping regression detection (first run?)")
        print(f"[INFO] To establish baseline, copy {args.results_file.name} to perf_baseline.json")
        sys.exit(0)
    
    # Load baseline
    try:
        with open(args.baseline) as f:
            baseline_results = json.load(f)
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in baseline file: {args.baseline}")
        print("[INFO] Baseline file may be corrupted - skipping regression check")
        sys.exit(0)
    
    # Perform analysis
    detector = RegressionDetector(current_results, baseline_results)
    analysis = detector.analyze()
    
    # Check if analysis had errors
    if 'error' in analysis:
        print(f"[WARN] Analysis incomplete: {analysis['error']}")
        print("[INFO] Skipping regression detection")
        sys.exit(0)
    
    detector.print_report()
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"[INFO] Regression report saved to {args.output}")
    
    # Exit with error code if regressions detected
    if detector.regressions:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
