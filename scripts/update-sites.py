#!/usr/bin/env python3
"""
PRD Propagator - Updates all sites based on a central PRD using Claude AI.

This script:
1. Reads the master PRD from prd.md
2. For each site in sites.json:
   - Clones the repository
   - Sends the current code + PRD to Claude
   - Applies Claude's suggested changes
   - Commits and pushes the changes
3. Lovable auto-deploys from the git push

Usage:
    python scripts/update-sites.py

Environment Variables:
    ANTHROPIC_API_KEY - Your Anthropic API key
    GH_PAT - GitHub Personal Access Token with repo access
    DRY_RUN - Set to 'true' to skip actual git operations
    SPECIFIC_SITE - If set, only update this specific site
"""

import anthropic
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional


# Configuration
MAX_WORKERS = 3  # Process 3 sites in parallel
MAX_FILE_SIZE = 50000  # Skip files larger than 50KB
ALLOWED_EXTENSIONS = {'.tsx', '.ts', '.jsx', '.js', '.css', '.html', '.json', '.md'}
SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '.next', '.cache'}


def setup_logging():
    """Create logs directory and return log file path."""
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return logs_dir / f'propagation_{timestamp}.log'


def log(message: str, log_file: Path):
    """Log message to both console and file."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    with open(log_file, 'a') as f:
        f.write(formatted + '\n')


def read_site_files(repo_path: Path) -> dict[str, str]:
    """Read all relevant source files from the repository."""
    site_files = {}
    
    for file in repo_path.rglob('*'):
        # Skip directories we don't care about
        if any(skip_dir in file.parts for skip_dir in SKIP_DIRS):
            continue
            
        if not file.is_file():
            continue
            
        if file.suffix not in ALLOWED_EXTENSIONS:
            continue
            
        # Skip large files
        if file.stat().st_size > MAX_FILE_SIZE:
            continue
            
        try:
            relative_path = str(file.relative_to(repo_path))
            site_files[relative_path] = file.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            pass
    
    return site_files


def update_site_with_claude(
    site_files: dict[str, str], 
    prd_content: str,
    site_name: str
) -> str:
    """Use Claude to analyze and update the site code based on the PRD."""
    
    client = anthropic.Anthropic()
    
    # Build context from current files (limit to avoid token limits)
    sorted_files = sorted(site_files.items(), key=lambda x: len(x[1]))
    total_chars = 0
    files_context_parts = []
    
    for path, content in sorted_files:
        if total_chars + len(content) > 100000:  # ~25K tokens limit for context
            break
        files_context_parts.append(f"=== {path} ===\n{content}")
        total_chars += len(content)
    
    files_context = "\n\n".join(files_context_parts)
    
    prompt = f"""You are updating a website codebase based on a Product Requirements Document (PRD).

## Site Name: {site_name}

## Product Requirements Document:
{prd_content}

## Current Site Code:
{files_context}

## Your Task:
1. Review the current code structure and understand what exists
2. Compare against the PRD requirements
3. Make necessary updates to align the site with the PRD
4. Preserve site-specific content (names, contact info, images) while updating structure/features

## Output Format:
For each file that needs changes, output in this EXACT format:

--- FILE: path/to/file.tsx ---
[complete file content here]
--- END FILE ---

Rules:
- Only output files that need actual changes
- Include the COMPLETE file content (not partial)
- Maintain existing styling patterns and code conventions
- Keep all imports and dependencies intact
- If a file is fine as-is, don't include it

If no changes are needed, respond with: NO_CHANGES_NEEDED"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16384,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


def parse_file_changes(claude_response: str) -> dict[str, str]:
    """Parse Claude's response into a dictionary of file paths and contents."""
    if "NO_CHANGES_NEEDED" in claude_response:
        return {}
    
    changes = {}
    pattern = r'--- FILE: (.+?) ---\n(.*?)--- END FILE ---'
    matches = re.findall(pattern, claude_response, re.DOTALL)
    
    for file_path, content in matches:
        file_path = file_path.strip()
        content = content.strip()
        if file_path and content:
            changes[file_path] = content
    
    return changes


def apply_changes(repo_path: Path, changes: dict[str, str], log_file: Path):
    """Write the file changes to disk."""
    for file_path, content in changes.items():
        full_path = repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        log(f"    Updated: {file_path}", log_file)


def process_single_site(
    site: dict,
    prd_content: str,
    gh_token: str,
    dry_run: bool,
    log_file: Path
) -> dict:
    """Process a single site - clone, update, push."""
    repo_name = site['repo']
    site_name = site.get('name', repo_name)
    result = {'repo': repo_name, 'status': 'unknown', 'changes': 0, 'error': None}
    
    log(f"\n{'='*60}", log_file)
    log(f"Processing: {site_name} ({repo_name})", log_file)
    log('='*60, log_file)
    
    repo_path = Path(f"temp_{repo_name.replace('/', '_')}")
    
    try:
        # Clean up any existing temp directory
        if repo_path.exists():
            subprocess.run(['rm', '-rf', str(repo_path)], check=True)
        
        # Clone the repository
        log(f"  Cloning repository...", log_file)
        repo_url = f"https://x-access-token:{gh_token}@github.com/{repo_name}.git"
        subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(repo_path)],
            check=True,
            capture_output=True
        )
        
        # Read current site files
        log(f"  Reading site files...", log_file)
        site_files = read_site_files(repo_path)
        log(f"  Found {len(site_files)} source files", log_file)
        
        # Get Claude to analyze and update
        log(f"  Analyzing with Claude AI...", log_file)
        claude_response = update_site_with_claude(site_files, prd_content, site_name)
        
        # Parse the changes
        changes = parse_file_changes(claude_response)
        result['changes'] = len(changes)
        
        if not changes:
            log(f"  ⏭️  No changes needed", log_file)
            result['status'] = 'no_changes'
            return result
        
        log(f"  Found {len(changes)} files to update", log_file)
        
        if dry_run:
            log(f"  🔍 DRY RUN - Would update: {list(changes.keys())}", log_file)
            result['status'] = 'dry_run'
            return result
        
        # Apply the changes
        apply_changes(repo_path, changes, log_file)
        
        # Commit and push
        log(f"  Committing changes...", log_file)
        
        # Configure git
        subprocess.run(
            ['git', 'config', 'user.email', 'prd-propagator@automated.bot'],
            cwd=repo_path, check=True
        )
        subprocess.run(
            ['git', 'config', 'user.name', 'PRD Propagator'],
            cwd=repo_path, check=True
        )
        
        subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
        
        commit_result = subprocess.run(
            ['git', 'commit', '-m', 'chore: sync with PRD update\n\nAutomated update from PRD propagator'],
            cwd=repo_path,
            capture_output=True
        )
        
        if commit_result.returncode == 0:
            log(f"  Pushing to remote...", log_file)
            subprocess.run(['git', 'push'], cwd=repo_path, check=True)
            log(f"  ✅ Successfully updated {repo_name}", log_file)
            result['status'] = 'success'
        else:
            log(f"  ⚠️  No changes to commit (files unchanged)", log_file)
            result['status'] = 'no_changes'
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        log(f"  ❌ Git error: {error_msg}", log_file)
        result['status'] = 'error'
        result['error'] = error_msg
        
    except anthropic.APIError as e:
        log(f"  ❌ Claude API error: {e}", log_file)
        result['status'] = 'error'
        result['error'] = str(e)
        
    except Exception as e:
        log(f"  ❌ Unexpected error: {e}", log_file)
        result['status'] = 'error'
        result['error'] = str(e)
        
    finally:
        # Clean up
        if repo_path.exists():
            subprocess.run(['rm', '-rf', str(repo_path)], capture_output=True)
    
    return result


def main():
    """Main entry point."""
    log_file = setup_logging()
    log("🚀 PRD Propagator Starting", log_file)
    
    # Load configuration
    prd_path = Path('prd.md')
    sites_path = Path('sites.json')
    
    if not prd_path.exists():
        log("❌ Error: prd.md not found", log_file)
        sys.exit(1)
        
    if not sites_path.exists():
        log("❌ Error: sites.json not found", log_file)
        sys.exit(1)
    
    prd_content = prd_path.read_text()
    sites_data = json.loads(sites_path.read_text())
    sites = [s for s in sites_data['sites'] if s.get('enabled', True)]
    
    # Environment variables
    gh_token = os.environ.get('GH_PAT')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'
    specific_site = os.environ.get('SPECIFIC_SITE', '').strip()
    
    if not gh_token:
        log("❌ Error: GH_PAT environment variable not set", log_file)
        sys.exit(1)
        
    if not anthropic_key:
        log("❌ Error: ANTHROPIC_API_KEY environment variable not set", log_file)
        sys.exit(1)
    
    # Filter to specific site if requested
    if specific_site:
        sites = [s for s in sites if s['repo'] == specific_site]
        if not sites:
            log(f"❌ Error: Site '{specific_site}' not found in sites.json", log_file)
            sys.exit(1)
    
    log(f"📋 PRD loaded ({len(prd_content)} chars)", log_file)
    log(f"🌐 {len(sites)} sites to update", log_file)
    
    if dry_run:
        log("🔍 DRY RUN MODE - No changes will be pushed", log_file)
    
    # Process sites (parallel for speed)
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                process_single_site, 
                site, 
                prd_content, 
                gh_token, 
                dry_run,
                log_file
            ): site 
            for site in sites
        }
        
        for future in as_completed(futures):
            results.append(future.result())
    
    # Summary
    log("\n" + "="*60, log_file)
    log("📊 SUMMARY", log_file)
    log("="*60, log_file)
    
    success = sum(1 for r in results if r['status'] == 'success')
    no_changes = sum(1 for r in results if r['status'] == 'no_changes')
    errors = sum(1 for r in results if r['status'] == 'error')
    dry_runs = sum(1 for r in results if r['status'] == 'dry_run')
    
    log(f"  ✅ Success: {success}", log_file)
    log(f"  ⏭️  No changes needed: {no_changes}", log_file)
    log(f"  🔍 Dry run: {dry_runs}", log_file)
    log(f"  ❌ Errors: {errors}", log_file)
    
    if errors > 0:
        log("\nFailed sites:", log_file)
        for r in results:
            if r['status'] == 'error':
                log(f"  - {r['repo']}: {r['error']}", log_file)
    
    log(f"\n✨ Propagation complete!", log_file)
    
    # Exit with error if any failures
    sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
