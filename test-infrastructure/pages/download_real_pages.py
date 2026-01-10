#!/usr/bin/env python3
"""
Download real-world web pages for performance testing.
Strips external resources to test rendering only.
"""

import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# Top websites for testing (diverse content types)
TOP_SITES = [
    "https://example.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://wikipedia.org",
    "https://reddit.com",
    "https://twitter.com",
    "https://medium.com",
    "https://news.ycombinator.com",
    "https://docs.python.org",
    "https://developer.mozilla.org",
]


def download_and_sanitize(url, output_dir):
    """Download a webpage and sanitize it for offline rendering tests."""
    
    print(f"Downloading {url}...")
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'HiWave Performance Test Bot'
        })
        response.raise_for_status()
    except Exception as e:
        print(f"  ❌ Failed to download: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove scripts (we're testing rendering, not JS execution)
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove external stylesheets (inline them if needed)
    for link in soup.find_all('link', rel='stylesheet'):
        link.decompose()
    
    # Remove iframes
    for iframe in soup.find_all('iframe'):
        iframe.decompose()
    
    # Convert image sources to placeholders
    for img in soup.find_all('img'):
        img['src'] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23ddd"/%3E%3C/svg%3E'
    
    # Remove external links (prevent accidental navigation)
    for a in soup.find_all('a', href=True):
        a['href'] = '#'
    
    # Get domain for filename
    domain = urlparse(url).netloc.replace('www.', '')
    filename = f"{domain}.html"
    filepath = output_dir / filename
    
    # Write sanitized HTML
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    # Estimate complexity
    all_elements = soup.find_all(True)
    element_count = len(all_elements)
    
    # Estimate DOM depth
    def get_depth(elem, current=0):
        if not elem.find_all(True, recursive=False):
            return current
        return max(get_depth(child, current + 1) for child in elem.find_all(True, recursive=False))
    
    dom_depth = get_depth(soup.body) if soup.body else 0
    
    print(f"  ✅ Saved to {filename} (elements={element_count}, depth={dom_depth})")
    
    return {
        "file": filename,
        "name": f"Real World: {domain}",
        "url": url,
        "complexity": {
            "dom_depth": dom_depth,
            "element_count": element_count,
            "css_rules": 0,  # Unknown for real pages
        }
    }


def main():
    """Download and process real-world pages."""
    
    script_dir = Path(__file__).parent
    output_dir = script_dir / "real-world-pages"
    output_dir.mkdir(exist_ok=True)
    
    manifest = {"pages": []}
    
    for url in TOP_SITES:
        result = download_and_sanitize(url, output_dir)
        if result:
            manifest["pages"].append(result)
    
    # Write manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Downloaded {len(manifest['pages'])} real-world pages")
    print(f"📄 Manifest written to {manifest_path}")
    print(f"📁 Pages in {output_dir}")


if __name__ == "__main__":
    main()
