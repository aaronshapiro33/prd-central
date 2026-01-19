#!/usr/bin/env python3
"""
Helper script to add new sites to sites.json

Usage:
    python scripts/add-site.py aaronshapiro33/my-new-site "My New Site"
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/add-site.py <repo> [name]")
        print("Example: python scripts/add-site.py aaronshapiro33/my-site 'My Site Name'")
        sys.exit(1)
    
    repo = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else repo.split('/')[-1]
    
    sites_path = Path('sites.json')
    
    if not sites_path.exists():
        data = {"sites": []}
    else:
        data = json.loads(sites_path.read_text())
    
    # Check if site already exists
    existing = [s for s in data['sites'] if s['repo'] == repo]
    if existing:
        print(f"❌ Site '{repo}' already exists in sites.json")
        sys.exit(1)
    
    # Add new site
    data['sites'].append({
        "repo": repo,
        "name": name,
        "enabled": True
    })
    
    # Save
    sites_path.write_text(json.dumps(data, indent=2))
    print(f"✅ Added site: {name} ({repo})")
    print(f"   Total sites: {len(data['sites'])}")


if __name__ == '__main__':
    main()
