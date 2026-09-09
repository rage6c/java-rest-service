#!/usr/bin/env python3
"""Build the consolidated standard from README metadata and numbered topics."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render():
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    intro = readme.split('## Reading options\n', 1)[0]
    index = '## Topic index\n' + readme.split('## Topic index\n', 1)[1].split(
        '\n## Documentation sources', 1
    )[0]
    parts = [intro, index]
    for topic in sorted(ROOT.glob('[0-9][0-9]-*.md')):
        lines = []
        in_fence = False
        for line in topic.read_text(encoding='utf-8').splitlines():
            if line.startswith('```'):
                in_fence = not in_fence
            if not in_fence and line.startswith('#'):
                line = '#' + line
            lines.append(line)
        parts.append('\n\n---\n\n' + '\n'.join(lines))
    return ''.join(parts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if output is stale')
    args = parser.parse_args()
    target = ROOT / 'JAVA-SERVICE-CODING-STANDARD.md'
    expected = render()
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != expected:
            raise SystemExit('Consolidated standard is stale; run scripts/build-standard.py')
        print('Consolidated standard matches all topic files.')
    else:
        target.write_text(expected, encoding='utf-8')
        print('Regenerated JAVA-SERVICE-CODING-STANDARD.md')


if __name__ == '__main__':
    main()
