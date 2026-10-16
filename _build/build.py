"""Inlines generated illustrations into index.html.

Placeholders look like <!--il:name-->...<!--/il--> (optionally <!--il:name:plain--> to strip
callout markers). Re-running replaces the content between the markers, so it is idempotent.
"""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(ROOT, '_build', 'illus.py')], check=True, stdout=subprocess.DEVNULL)
html_path = os.path.join(ROOT, 'index.html')
html = open(html_path, encoding='utf-8').read()

def strip_marks(svg):
    svg = re.sub(r'<path class="il-lead"[^>]*/>', '', svg)
    svg = re.sub(r'<circle class="il-dot"[^>]*/>', '', svg)
    svg = re.sub(r'<g class="il-mark"[^>]*>.*?</g>', '', svg)
    return svg

def sub(m):
    name, mode = m.group(1), m.group(2)
    svg = open(os.path.join(ROOT, '_build', 'out', name + '.svg'), encoding='utf-8').read()
    if mode == 'plain':
        svg = strip_marks(svg)
    return f'<!--il:{name}{":" + mode if mode else ""}-->{svg}<!--/il-->'

html, n = re.subn(r'<!--il:([\w-]+)(?::(\w+))?-->.*?<!--/il-->', sub, html, flags=re.S)
open(html_path, 'w', encoding='utf-8').write(html)
print('inlined', n)
