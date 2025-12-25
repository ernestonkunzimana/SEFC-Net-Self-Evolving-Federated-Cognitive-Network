import os
import re
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
pdf_path = workspace_root / "SEFC-Net.pdf"
out_dir = workspace_root / "scripts"
out_dir.mkdir(parents=True, exist_ok=True)

pdf_text_file = out_dir / "pdf_text.txt"
expected_manifest = out_dir / "expected_manifest.txt"
current_manifest = out_dir / "current_manifest.txt"
report_file = out_dir / "compare_report.txt"
missing_file = out_dir / "missing.txt"
extra_file = out_dir / "extra.txt"

# Try to import pypdf
try:
    from pypdf import PdfReader
except Exception as e:
    print("pypdf not installed. Please run: python -m pip install pypdf")
    sys.exit(2)

if not pdf_path.exists():
    print(f"PDF not found at {pdf_path}")
    sys.exit(3)

# Extract text
reader = PdfReader(str(pdf_path))
pages = []
for p in reader.pages:
    try:
        pages.append(p.extract_text() or "")
    except Exception:
        pages.append("")
text = "\n".join(pages)
pdf_text_file.write_text(text, encoding="utf-8")

# Heuristic extraction of file-like strings from pdf text
# Matches words with extensions or common filenames (Dockerfile, README, .gitignore)
pattern = re.compile(r"[\w\- ./\\]+?(?:\.[A-Za-z0-9_\-]+|Dockerfile|README|LICENSE|Makefile|\.gitignore)")
matches = pattern.findall(text)

candidates = set()
for m in matches:
    s = m.strip()
    # remove trailing punctuation
    s = s.strip('.,;:\\"')
    # Normalize Windows backslashes to forward slashes
    s = s.replace('\\', '/')
    # Remove leading bullets or line markers
    s = re.sub(r"^[\-•\u2022\*\s]+", "", s)
    # Keep only relative paths or bare filenames
    if len(s) > 0 and len(s) < 300:
        candidates.add(s)

# Further filter: keep items that look like files or top-level folders
keep = set()
for c in candidates:
    base = os.path.basename(c)
    if '.' in base or base.lower() in ('dockerfile', 'readme', 'license', '.gitignore', 'makefile'):
        keep.add(c)
    else:
        # also accept folder-like tokens ending with '/'
        if c.endswith('/') or c.endswith('\\'):
            keep.add(c.rstrip('/\\'))

# Normalize and dedupe; convert to posix relative paths where possible
normalized = set()
for p in keep:
    p2 = p.strip()
    # remove surrounding quotes
    p2 = p2.strip('\"\'')
    p2 = p2.strip()
    # if path is absolute, make it relative
    p2 = p2.replace('\\', '/')
    # Remove leading ./
    if p2.startswith('./'):
        p2 = p2[2:]
    normalized.add(p2)

# Write expected manifest
with expected_manifest.open('w', encoding='utf-8') as f:
    for p in sorted(normalized):
        f.write(p + '\n')

# Build current manifest (all files under workspace root, relative)
current_files = []
for root, dirs, files in os.walk(workspace_root):
    # skip .git and __pycache__ by default
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]
    for fn in files:
        fp = os.path.join(root, fn)
        rel = os.path.relpath(fp, workspace_root).replace('\\', '/')
        current_files.append(rel)
current_files = sorted(current_files)
with current_manifest.open('w', encoding='utf-8') as f:
    for p in current_files:
        f.write(p + '\n')

# Compare sets
expected_set = set([p for p in (str(x).strip() for x in expected_manifest.read_text(encoding='utf-8').splitlines()) if p])
current_set = set(current_files)

# Try to map some expected names to actual files when only basename provided
expanded_expected = set()
for e in expected_set:
    if '/' in e:
        expanded_expected.add(e)
    else:
        # find any current file with this basename
        for c in current_set:
            if os.path.basename(c) == e:
                expanded_expected.add(c)

defn_expected = set(expanded_expected)
missing = sorted(list(defn_expected - current_set))
extra = sorted(list(current_set - defn_expected))

with missing_file.open('w', encoding='utf-8') as f:
    for p in missing:
        f.write(p + '\n')
with extra_file.open('w', encoding='utf-8') as f:
    for p in extra:
        f.write(p + '\n')

# Write report
with report_file.open('w', encoding='utf-8') as f:
    f.write('SEFC-Net PDF vs Workspace comparison\n')
    f.write('Workspace root: ' + str(workspace_root) + '\n')
    f.write('\n')
    f.write(f'Extracted {len(defn_expected)} expected items from PDF (after basename expansion)\n')
    f.write(f'Current workspace files: {len(current_set)}\n')
    f.write(f'Missing: {len(missing)}\n')
    f.write(f'Extra (present in workspace but not listed in PDF-derived manifest): {len(extra)}\n')
    f.write('\n')
    if missing:
        f.write('--- Missing files ---\n')
        for p in missing:
            f.write(p + '\n')
        f.write('\n')
    if extra:
        f.write('--- Extra files ---\n')
        # show only first 200 entries to keep report small
        for p in extra[:200]:
            f.write(p + '\n')
        if len(extra) > 200:
            f.write('... (truncated)\n')

print('Comparison complete.')
print('Report written to:', report_file)
print('Missing file count:', len(missing))
print('Extra file count:', len(extra))
print('\nFiles produced:')
print(' -', expected_manifest)
print(' -', current_manifest)
print(' -', missing_file)
print(' -', extra_file)
print(' -', report_file)
