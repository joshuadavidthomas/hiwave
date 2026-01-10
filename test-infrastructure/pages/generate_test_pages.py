#!/usr/bin/env python3
"""
Generate synthetic test pages with varying complexity for performance testing.
"""

import json
import os
from pathlib import Path


def generate_html_page(dom_depth, element_count, css_rules):
    """Generate an HTML page with specified complexity."""
    
    # Generate CSS
    css = []
    for i in range(css_rules):
        selector = f".class-{i}"
        properties = [
            f"margin: {i}px;",
            f"padding: {i * 2}px;",
            f"font-size: {12 + (i % 10)}px;",
        ]
        css.append(f"{selector} {{ {' '.join(properties)} }}")
    
    css_content = "\n".join(css)
    
    # Generate nested DOM structure
    def create_nested_divs(depth, elements_per_level):
        if depth == 0:
            return "<p>Leaf content</p>"
        
        divs = []
        for i in range(elements_per_level):
            class_name = f"class-{i % css_rules}"
            inner = create_nested_divs(depth - 1, max(1, elements_per_level // 2))
            divs.append(f'<div class="{class_name}">\n  {inner}\n</div>')
        
        return "\n".join(divs)
    
    elements_per_level = max(2, int((element_count / dom_depth) ** 0.5))
    body_content = create_nested_divs(dom_depth, elements_per_level)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page - Depth:{dom_depth} Elements:{element_count} CSS:{css_rules}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <h1>Performance Test Page</h1>
    <div class="container">
{body_content}
    </div>
</body>
</html>"""
    
    return html


def main():
    """Generate test pages with various complexity levels."""
    
    script_dir = Path(__file__).parent
    pages_dir = script_dir
    pages_dir.mkdir(exist_ok=True)
    
    # Define complexity levels
    test_configs = [
        # (dom_depth, element_count, css_rules, name)
        (5, 50, 10, "simple"),
        (5, 100, 25, "simple-medium"),
        (10, 200, 50, "medium"),
        (10, 500, 100, "medium-complex"),
        (15, 1000, 200, "complex"),
        (20, 2000, 500, "very-complex"),
        (30, 5000, 1000, "extreme"),
        # Edge cases
        (50, 100, 10, "deep-shallow"),  # Deep but few elements
        (5, 10000, 50, "shallow-wide"),  # Shallow but many elements
        (10, 1000, 2000, "css-heavy"),  # Heavy CSS
    ]
    
    manifest = {"pages": []}
    
    for depth, elements, css, name in test_configs:
        filename = f"test-page-{name}.html"
        filepath = pages_dir / filename
        
        print(f"Generating {filename} (depth={depth}, elements~{elements}, css={css})...")
        
        html = generate_html_page(depth, elements, css)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        manifest["pages"].append({
            "file": filename,
            "name": f"Test Page: {name}",
            "complexity": {
                "dom_depth": depth,
                "element_count": elements,
                "css_rules": css,
            }
        })
    
    # Write manifest
    manifest_path = pages_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Generated {len(test_configs)} test pages")
    print(f"📄 Manifest written to {manifest_path}")
    print(f"📁 Pages in {pages_dir}")


if __name__ == "__main__":
    main()
