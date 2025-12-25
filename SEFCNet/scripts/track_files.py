"""
Track and report on repository file structure.
Creates a manifest of current files and generates a report.

Usage:
    python track_files.py [--exclude venv,__pycache__,.git]
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

def get_file_category(filepath):
    """Categorize a file based on its extension and path."""
    path = Path(filepath)
    if path.name.startswith('.'):
        return 'dotfiles'
    
    ext = path.suffix.lower()
    if ext in {'.py'}:
        if 'tests' in path.parts:
            return 'tests'
        return 'python'
    elif ext in {'.md', '.rst'}:
        return 'documentation'
    elif ext in {'.yml', '.yaml', '.json', '.toml', '.ini'}:
        return 'configuration'
    elif ext in {'.txt'}:
        if path.name == 'requirements.txt':
            return 'configuration'
        return 'text'
    elif ext in {'.pdf', '.docx'}:
        return 'documentation'
    elif ext in {'.html', '.css', '.js'}:
        return 'web'
    elif ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg'}:
        return 'assets'
    elif 'Dockerfile' in path.name:
        return 'infrastructure'
    elif ext in {'.sh', '.ps1', '.bat', '.cmd'}:
        return 'scripts'
    return 'other'

def create_manifest(root_dir, exclude=None):
    """Create a manifest of all files in the repository."""
    if exclude is None:
        exclude = {'venv', '__pycache__', '.git', '.pytest_cache'}
    
    manifest = []
    categories = defaultdict(list)
    
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude]
        
        for file in files:
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, root_dir)
            
            # Skip files in excluded dirs (deeper check)
            if any(x in relpath.split(os.sep) for x in exclude):
                continue
                
            category = get_file_category(filepath)
            manifest.append(relpath)
            categories[category].append(relpath)
    
    return sorted(manifest), categories

def write_manifest(manifest, categories, root_dir):
    """Write manifest and report files."""
    out_dir = Path(root_dir) / 'scripts'
    out_dir.mkdir(exist_ok=True)
    
    # Write full manifest
    manifest_file = out_dir / 'manifest.txt'
    with manifest_file.open('w', encoding='utf-8') as f:
        for filepath in manifest:
            f.write(filepath + '\n')
    
    # Write categorized report
    report_file = out_dir / 'manifest_report.txt'
    with report_file.open('w', encoding='utf-8') as f:
        f.write(f'Repository File Manifest Report\n')
        f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'Total files: {len(manifest)}\n\n')
        
        for category, files in sorted(categories.items()):
            f.write(f'\n{category.upper()} ({len(files)} files)\n')
            f.write('-' * (len(category) + 15) + '\n')
            for filepath in sorted(files):
                f.write(f'  {filepath}\n')
    
    print(f'Manifest written to: {manifest_file}')
    print(f'Report written to: {report_file}')
    print('\nSummary:')
    for category, files in sorted(categories.items()):
        print(f'  {category}: {len(files)} files')

def main():
    """Main entry point."""
    # Get repository root (parent of this script)
    root_dir = Path(__file__).resolve().parent.parent
    
    # Default exclusions
    exclude = {'venv', '__pycache__', '.git', '.pytest_cache'}
    
    # Parse command line args for additional exclusions
    if len(sys.argv) > 1:
        if sys.argv[1] == '--exclude':
            exclude.update(sys.argv[2].split(','))
    
    manifest, categories = create_manifest(root_dir, exclude)
    write_manifest(manifest, categories, root_dir)

if __name__ == '__main__':
    main()