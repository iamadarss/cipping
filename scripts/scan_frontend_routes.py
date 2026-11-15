# scripts/scan_frontend_routes.py
import re
import os
from pathlib import Path
import sys

# Add parent to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import create_app

def scan():
    app = create_app()
    # Collect all registered route rules
    rules = []
    for r in app.url_map.iter_rules():
        # normalize rule to regex
        # e.g. /editor/api/projects/<int:proj_id>/editor-state -> /editor/api/projects/[^/]+/editor-state
        rule_str = r.rule
        regex_pattern = re.sub(r'<[^>]+>', r'[^/]+', rule_str)
        regex_pattern = f"^{regex_pattern}$"
        rules.append((re.compile(regex_pattern), rule_str, r.methods))

    root_dir = Path(__file__).parent.parent
    frontend_files = []
    for ext in ['*.js', '*.html']:
        for p in (root_dir / 'static').rglob(ext):
            if '_archive' not in str(p):
                frontend_files.append(p)
        for p in (root_dir / 'templates').rglob(ext):
            frontend_files.append(p)

    fetch_pattern = re.compile(r"""(?:fetch|axios\.(?:get|post|put|delete))\s*\(\s*[`'"]([^`'"]+)[`'"]""")

    total_fetches = 0
    matched = 0
    broken = []

    for fpath in frontend_files:
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            for match in fetch_pattern.finditer(line):
                url = match.group(1).strip()
                if not url.startswith(('/', 'http')):
                    continue
                if url.startswith(('http://', 'https://')):
                    continue

                total_fetches += 1
                # Clean URL of template strings e.g. ${...}
                clean_url = re.sub(r'\$\{[^}]+\}', '1', url)
                clean_url = clean_url.split('?')[0]

                # Check if it matches any registered rule
                is_match = any(pattern.match(clean_url) for pattern, _, _ in rules)
                if is_match:
                    matched += 1
                else:
                    broken.append((fpath.relative_to(root_dir), line_no, url, clean_url))

    print(f"Scanned {len(frontend_files)} frontend files.")
    print(f"Total internal fetch calls: {total_fetches}")
    print(f"Matched: {matched}")
    print(f"Broken / Unmatched: {len(broken)}")
    for f, l, raw, norm in broken:
        print(f"  [404] {f}:{l} -> {raw} (normalized: {norm})")

    return len(broken)

if __name__ == '__main__':
    errs = scan()
    sys.exit(0 if errs == 0 else 1)
