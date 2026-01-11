# Code Churn Analysis Report

**Generated:** 2026-01-10 19:55:59

## Overview

- **Repositories Analyzed:** hiwave-macos, hiwave-linux, hiwave-windows
- **Total Files Modified:** 1582
- **Total Commits Analyzed:** 3600
- **Cross-Repo Files:** 611
- **Line Range Bucket Size:** 50 lines

## Repository Statistics

**Total lines across all repos:** 1,209,136

| Repository | Total Lines | Total Files | Commits | Branch |
|------------|-------------|-------------|---------|--------|
| hiwave-macos | 845,058 | 1,165 | 90 | master |
| hiwave-linux | 136,568 | 515 | 4 | master |
| hiwave-windows | 227,510 | 638 | 90 | master |

### Lines by File Type

- **hiwave-macos:** .json (380,522), .js (128,578), .rs (77,459), .ppm (67,340), .ts (57,272)
- **hiwave-linux:** .rs (66,969), .md (12,907), .cpp (12,567), .html (11,642), .h (10,965)
- **hiwave-windows:** .rs (70,987), .json (66,714), .html (18,759), .md (14,553), .cpp (12,567)

## Top 10 Highest-Churn Files

| Rank | File | Churn Score | Modifications | Repos |
|------|------|-------------|---------------|-------|
| 1 | `Cargo.lock` | 159 | 53 | hiwave-linux, hiwave-macos, hiwave-windows |
| 2 | `crates/rustkit-engine/src/lib.rs` | 147 | 49 | hiwave-linux, hiwave-macos, hiwave-windows |
| 3 | `Cargo.toml` | 108 | 36 | hiwave-linux, hiwave-macos, hiwave-windows |
| 4 | `crates/rustkit-layout/src/lib.rs` | 90 | 30 | hiwave-linux, hiwave-macos, hiwave-windows |
| 5 | `crates/hiwave-app/src/main.rs` | 78 | 26 | hiwave-linux, hiwave-macos, hiwave-windows |
| 6 | `crates/rustkit-css/src/lib.rs` | 63 | 21 | hiwave-linux, hiwave-macos, hiwave-windows |
| 7 | `crates/hiwave-app/Cargo.toml` | 51 | 17 | hiwave-linux, hiwave-macos, hiwave-windows |
| 8 | `README.md` | 45 | 15 | hiwave-linux, hiwave-macos, hiwave-windows |
| 9 | `crates/rustkit-renderer/src/lib.rs` | 42 | 14 | hiwave-linux, hiwave-macos, hiwave-windows |
| 10 | `crates/rustkit-viewhost/src/lib.rs` | 42 | 14 | hiwave-linux, hiwave-macos, hiwave-windows |

## Top 10 Highest-Churn Line Ranges

| Rank | File | Line Range | Touches | Repos |
|------|------|------------|---------|-------|
| 1 | `...y-baseline/captures/sticky-scroll.ppm` | 0-50 | 163 | hiwave-macos |
| 2 | `parity-baseline/baseline_report.json` | 50-100 | 150 | hiwave-macos |
| 3 | `...y-baseline/captures/css-selectors.ppm` | 150-200 | 147 | hiwave-macos |
| 4 | `...y-baseline/captures/sticky-scroll.ppm` | 50-100 | 138 | hiwave-macos |
| 5 | `...y-baseline/captures/sticky-scroll.ppm` | 100-150 | 124 | hiwave-macos |
| 6 | `...y-baseline/captures/css-selectors.ppm` | 250-300 | 118 | hiwave-macos |
| 7 | `...y-baseline/captures/css-selectors.ppm` | 300-350 | 116 | hiwave-macos |
| 8 | `...y-baseline/captures/form-elements.ppm` | 0-50 | 111 | hiwave-macos |
| 9 | `parity-baseline/baseline_report.json` | 0-50 | 108 | hiwave-macos |
| 10 | `...y-baseline/captures/css-selectors.ppm` | 100-150 | 104 | hiwave-macos |

## Cross-Repository Files

Files modified across multiple repositories may indicate:
- Core shared functionality
- Platform-specific adaptations of common code
- Potential candidates for refactoring into shared modules

| File | Modifications | Repos | Lines +/- |
|------|---------------|-------|-----------|
| `Cargo.lock` | 53 | hiwave-linux, hiwave-macos, hiwave-windows | +27029/-2774 |
| `crates/rustkit-engine/src/lib.rs` | 49 | hiwave-linux, hiwave-macos, hiwave-windows | +9858/-444 |
| `Cargo.toml` | 36 | hiwave-linux, hiwave-macos, hiwave-windows | +419/-50 |
| `crates/rustkit-layout/src/lib.rs` | 30 | hiwave-linux, hiwave-macos, hiwave-windows | +7341/-251 |
| `crates/hiwave-app/src/main.rs` | 26 | hiwave-linux, hiwave-macos, hiwave-windows | +12652/-751 |
| `crates/rustkit-css/src/lib.rs` | 21 | hiwave-linux, hiwave-macos, hiwave-windows | +4648/-123 |
| `crates/hiwave-app/Cargo.toml` | 17 | hiwave-linux, hiwave-macos, hiwave-windows | +242/-33 |
| `README.md` | 15 | hiwave-linux, hiwave-macos, hiwave-windows | +1138/-217 |
| `crates/rustkit-renderer/src/lib.rs` | 14 | hiwave-linux, hiwave-macos, hiwave-windows | +4474/-122 |
| `crates/rustkit-viewhost/src/lib.rs` | 14 | hiwave-linux, hiwave-macos, hiwave-windows | +4319/-165 |
| `crates/rustkit-renderer/src/glyph.rs` | 13 | hiwave-linux, hiwave-macos, hiwave-windows | +2257/-69 |
| `.gitignore` | 12 | hiwave-linux, hiwave-macos, hiwave-windows | +176/-11 |
| `crates/rustkit-compositor/src/lib.rs` | 12 | hiwave-linux, hiwave-macos, hiwave-windows | +1811/-30 |
| `crates/rustkit-dom/src/lib.rs` | 12 | hiwave-linux, hiwave-macos, hiwave-windows | +2759/-120 |
| `.ai/roadmap_index.json` | 18 | hiwave-linux, hiwave-windows | +421/-267 |

## Divergent Modification Patterns

Files with significantly different modification patterns across repos:

### `Cargo.lock`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 10 | 134 |
| hiwave-windows | 42 | 148 |

### `crates/rustkit-engine/src/lib.rs`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 30 | 60 |
| hiwave-windows | 18 | 22 |

### `crates/hiwave-app/src/main.rs`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 11 | 34 |
| hiwave-windows | 14 | 44 |

### `websuite/captures/article-typography.ppm`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-macos | 2 | 41 |
| hiwave-windows | 1 | 1 |

### `crates/rustkit-layout/src/lib.rs`

**Divergence Score:** 0.97

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 18 | 32 |
| hiwave-windows | 11 | 18 |

### `Cargo.toml`

**Divergence Score:** 0.97

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 4 | 2 |
| hiwave-windows | 31 | 3 |

### `crates/rustkit-canvas/src/lib.rs`

**Divergence Score:** 0.97

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 1 | 1 |
| hiwave-windows | 2 | 29 |

### `crates/rustkit-css/src/lib.rs`

**Divergence Score:** 0.96

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 13 | 21 |
| hiwave-windows | 7 | 13 |

### `crates/rustkit-renderer/src/lib.rs`

**Divergence Score:** 0.96

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 11 | 24 |
| hiwave-windows | 2 | 6 |

### `crates/rustkit-viewhost/src/lib.rs`

**Divergence Score:** 0.95

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-linux | 1 | 1 |
| hiwave-macos | 6 | 7 |
| hiwave-windows | 7 | 16 |

## Recommendations

Based on the churn analysis, consider reviewing the following areas:

1. **High Churn Files - Architectural Review**
   - These files have been modified frequently across multiple repos. Consider reviewing their architecture for potential simplification or abstraction.
   - Files: `Cargo.lock`, `crates/rustkit-engine/src/lib.rs`, `Cargo.toml`, `crates/rustkit-layout/src/lib.rs`, `crates/hiwave-app/src/main.rs`

2. **Line Range Hotspots**
   - Specific line ranges in these files are being modified repeatedly. This may indicate ongoing bug fixes or feature adjustments in localized areas.
   - Files: `parity-baseline/captures/form-elements.ppm`, `parity-baseline/captures/css-selectors.ppm`, `parity-baseline/baseline_report.json`, `parity-baseline/captures/sticky-scroll.ppm`

3. **Cross-Platform Synchronization**
   - These files are modified across all repositories. Consider creating a shared module or ensuring changes are consistently applied.
   - Files: `Cargo.lock`, `crates/rustkit-engine/src/lib.rs`, `Cargo.toml`, `crates/rustkit-layout/src/lib.rs`, `crates/hiwave-app/src/main.rs`

4. **Divergent Development Patterns**
   - These files show different modification patterns across repos. This may indicate platform-specific implementations that could benefit from a unified approach.
   - Files: `Cargo.lock`, `crates/rustkit-engine/src/lib.rs`, `crates/hiwave-app/src/main.rs`, `websuite/captures/article-typography.ppm`, `crates/rustkit-layout/src/lib.rs`

5. **Many Single-Touch Files**
   - 858 files (54%) were only modified once. This is healthy and indicates stable code.

---

*This report was automatically generated by the Code Churn Analysis Tool.*