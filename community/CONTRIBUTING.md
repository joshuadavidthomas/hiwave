# Contributing to HiWave Browser

Thank you for your interest in contributing to HiWave! This guide will help you get started.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Parity Test Contributions](#parity-test-contributions)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Compatibility Reports](#compatibility-reports)
- [Documentation](#documentation)
- [Translations](#translations)
- [Pull Request Process](#pull-request-process)

---

## Ways to Contribute

### No Code Required

| Type | Description | Time Needed |
|------|-------------|-------------|
| Compatibility Report | Report websites that don't render correctly | 5 minutes |
| Bug Report | Report crashes, glitches, or unexpected behavior | 10 minutes |
| Feature Request | Suggest new features or improvements | 10 minutes |
| UI/UX Feedback | Share thoughts on design and usability | 15 minutes |

### Some Technical Knowledge

| Type | Description | Time Needed |
|------|-------------|-------------|
| Parity Test | Create minimal HTML that reproduces a rendering bug | 30-60 minutes |
| Documentation | Improve guides, FAQs, or tutorials | 30+ minutes |
| Translation | Translate UI strings to your language | 1+ hours |

---

## Parity Test Contributions

**Impact: HIGH** - These directly help us achieve pixel-perfect rendering.

### What is a Parity Test?

A parity test is a minimal HTML file that demonstrates a difference between HiWave's rendering and Chrome's rendering. Good parity tests:

- Are **minimal** - only the HTML/CSS needed to show the issue
- Are **isolated** - test one specific CSS feature or behavior
- Are **reproducible** - same result every time
- Include a **Chrome baseline** screenshot

### Creating a Parity Test

#### Step 1: Identify the Issue

Find a webpage where HiWave renders differently than Chrome. Common areas:

- CSS Selectors (specificity, combinators, pseudo-classes)
- Flexbox (alignment, wrapping, sizing)
- Grid (track sizing, placement)
- Images (object-fit, aspect-ratio, intrinsic sizing)
- Positioning (sticky, fixed, absolute)
- Forms (input styling, button sizing)

#### Step 2: Create Minimal Reproduction

Reduce the issue to the smallest possible HTML:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Parity Test: [Brief Description]</title>
  <style>
    /* Minimal CSS to reproduce the issue */
    .container {
      display: flex;
      justify-content: space-between;
    }
    .item {
      width: 100px;
      height: 100px;
      background: #007bff;
    }
  </style>
</head>
<body>
  <!-- Minimal HTML to reproduce the issue -->
  <div class="container">
    <div class="item">A</div>
    <div class="item">B</div>
    <div class="item">C</div>
  </div>
</body>
</html>
```

#### Step 3: Capture Chrome Baseline

1. Open your HTML file in Chrome
2. Set viewport to the specified size (usually 800x600 or 1280x800)
3. Take a screenshot (DevTools > Cmd+Shift+P > "Capture full size screenshot")
4. Save as `expected.png`

#### Step 4: Create Metadata

Create a `metadata.json` file:

```json
{
  "title": "Flexbox justify-content: space-between",
  "description": "Items should be evenly distributed with first item at start and last at end",
  "css_features": ["flexbox", "justify-content"],
  "author": "your-github-username",
  "viewport": {
    "width": 800,
    "height": 600
  },
  "chrome_version": "130.0.6723.91",
  "date_created": "2026-01-07",
  "severity": "major",
  "related_issues": []
}
```

#### Step 5: Submit PR

1. Fork this repository
2. Create folder: `parity-tests/submissions/your-test-name/`
3. Add files:
   - `index.html` - Your minimal reproduction
   - `expected.png` - Chrome screenshot
   - `metadata.json` - Test metadata
4. Open PR with title: `[Parity Test] Brief description`

### Parity Test Quality Checklist

Before submitting, verify:

- [ ] HTML is minimal (no unnecessary elements)
- [ ] CSS is minimal (no unnecessary properties)
- [ ] No external dependencies (fonts, images, scripts)
- [ ] No JavaScript (unless testing JS-related rendering)
- [ ] Chrome screenshot is sharp and correct viewport size
- [ ] metadata.json is complete
- [ ] Issue is reproducible (reload shows same problem)

### Test Naming Convention

```
feature-specific-issue/
  index.html
  expected.png
  metadata.json

Examples:
  flex-justify-space-between/
  grid-auto-rows-minmax/
  selector-nth-child-even/
  sticky-inside-overflow/
  image-object-fit-cover/
```

---

## Bug Reports

### What Makes a Good Bug Report

1. **Clear title** - Summarize the issue
2. **Steps to reproduce** - Exact steps to trigger the bug
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - OS version, HiWave version
6. **Screenshots/videos** - Visual evidence

### Bug Report Template

Use our [bug report template](.github/ISSUE_TEMPLATE/bug-report.yml) which guides you through all required information.

### Bug Severity Levels

| Severity | Description | Examples |
|----------|-------------|----------|
| Critical | Crash, data loss, security issue | Browser crashes on specific URL |
| Major | Feature broken, significant visual issue | Page layout completely wrong |
| Minor | Small visual glitch, workaround exists | Button slightly misaligned |
| Trivial | Cosmetic, minimal impact | Pixel-level difference |

---

## Feature Requests

### Before Submitting

1. Search existing requests to avoid duplicates
2. Check if it's already planned in our [roadmap](https://github.com/hiwavebrowser/community/discussions/categories/roadmap)

### Feature Request Template

- **Problem**: What problem does this solve?
- **Solution**: What's your proposed solution?
- **Alternatives**: What alternatives have you considered?
- **Context**: Any additional context or screenshots

---

## Compatibility Reports

Found a website that doesn't work in HiWave? Help us fix it!

### Quick Report

1. Go to [New Compatibility Report](https://github.com/hiwavebrowser/community/issues/new?template=compatibility-report.yml)
2. Enter the URL
3. Describe the issue
4. Add screenshots comparing HiWave vs Chrome

### What We Need

- URL of the problematic page
- Screenshot from HiWave
- Screenshot from Chrome (same viewport)
- Description of what's different
- Whether the site is usable or completely broken

### High-Priority Sites

We prioritize fixes for:
- Top 1000 websites (Alexa/Tranco rankings)
- Sites reported by multiple users
- Sites with complete breakage (vs minor visual differences)

---

## Documentation

Help improve our guides and documentation.

### Areas Needing Help

- **User Guides** - How to use HiWave features
- **FAQ** - Common questions and answers
- **Troubleshooting** - Solutions to common problems
- **Developer Guides** - Contributing to parity tests

### Documentation Style

- Use clear, simple language
- Include screenshots where helpful
- Keep paragraphs short
- Use headers and lists for scannability

---

## Translations

Help make HiWave available in your language.

### Getting Started

1. Check `localization/translations/` for existing work
2. Copy `en.json` to your language code (e.g., `fr.json`)
3. Translate strings, keeping placeholders intact
4. Submit PR

### Translation Guidelines

- Use formal/informal consistently (match language norms)
- Keep technical terms consistent (see `localization/glossary/`)
- Don't translate brand names (HiWave, RustKit)
- Test your translations fit in the UI

---

## Pull Request Process

### For Parity Tests

1. Ensure all files are in correct location
2. Verify metadata.json is valid JSON
3. Confirm Chrome screenshot matches specified viewport
4. Use descriptive PR title: `[Parity Test] flex-justify-content edge case`

### For Documentation

1. Check spelling and grammar
2. Verify all links work
3. Preview markdown rendering
4. Use descriptive PR title: `[Docs] Add FAQ about extension support`

### For Translations

1. Ensure JSON is valid
2. Check all strings are translated
3. Verify placeholders are preserved
4. Use descriptive PR title: `[i18n] Add French translation`

### Review Process

1. Automated checks run (JSON validation, file structure)
2. Maintainer reviews within 48-72 hours
3. Feedback provided if changes needed
4. Merged once approved

---

## Recognition

### Contributor Levels

| Level | Requirements | Benefits |
|-------|--------------|----------|
| **Contributor** | 1+ merged PR | Listed on contributors page |
| **Regular** | 5+ merged PRs | Beta access, Discord role |
| **Champion** | 20+ PRs or major impact | Early features, direct team access |

### Hall of Fame

Top contributors each month are featured in our release notes and on the website.

---

## Questions?

- **Discord**: [discord.gg/hiwave](https://discord.gg/hiwave)
- **Discussions**: [GitHub Discussions](https://github.com/hiwavebrowser/community/discussions)
- **Email**: community@hiwave.browser (for sensitive issues)

Thank you for helping make HiWave better!
