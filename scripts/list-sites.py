#!/usr/bin/env python3
"""
Helper script to list all sites in sites.json

Usage:
    python scripts/list-sites.py
"""

import json
from pathlib import Path


def main():
    sites_path = Path('sites.json')
    
    if not sites_path.exists():
        print("❌ sites.json not found")
        return
    
    data = json.loads(sites_path.read_text())
    sites = data.get('sites', [])
    
    print(f"\n📋 {len(sites)} sites registered:\n")
    print(f"{'#':<4} {'Status':<10} {'Name':<30} {'Repository'}")
    print("-" * 80)
    
    for i, site in enumerate(sites, 1):
        status = "✅ Enabled" if site.get('enabled', True) else "⏸️  Disabled"
        name = site.get('name', '-')[:28]
        repo = site.get('repo', '-')
        print(f"{i:<4} {status:<10} {name:<30} {repo}")
    
    enabled = sum(1 for s in sites if s.get('enabled', True))
    print(f"\n{enabled} enabled, {len(sites) - enabled} disabled")


if __name__ == '__main__':
    main()
