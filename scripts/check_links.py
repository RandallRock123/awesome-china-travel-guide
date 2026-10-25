"""Check this repository's inline Markdown links using Python's standard library."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import unquote, urldefrag, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def markdown_links(text):
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'`[^`]*`', '', text)
    return re.findall(r'\]\(([^\s)]+)\)', text)


def headings(text):
    used = set()
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        heading = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', heading)
        slug = re.sub(r'[^\w\-\s]', '', heading.lower()).replace(' ', '-')
        unique, n = slug, 0
        while unique in used:
            n += 1
            unique = f'{slug}-{n}'
        used.add(unique)
    return used


def check_http(url):
    result = {'url': url, 'ok': False}
    for attempt in range(3):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; ChinaRevealed-LinkCheck/1.0)'})
            with urlopen(req, timeout=25) as response:
                body = response.read(2_000_000).decode('utf-8', errors='replace')
                result.update(status=response.status, final_url=response.url, ok=200 <= response.status < 300)
                for tag in ('title', 'h1'):
                    match = re.search(fr'<{tag}\b[^>]*>(.*?)</{tag}>', body, re.S | re.I)
                    if match:
                        result[tag] = html.unescape(re.sub('<[^>]+>', '', match.group(1))).strip()
            return result
        except HTTPError as error:
            result.update(status=error.code, final_url=error.url, error=f'HTTP {error.code}')
            if error.code not in (429, 500, 502, 503, 504):
                break
        except Exception as error:
            result.update(error=f'{type(error).__name__}: {error}')
        if attempt < 2:
            time.sleep(2 * (attempt + 1))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', default='link-report.json')
    parser.add_argument('--site-only', action='store_true')
    args = parser.parse_args()
    urls, local = set(), []
    for name in ('README.md', 'CONTRIBUTING.md'):
        source = ROOT / name
        for link in markdown_links(source.read_text(encoding='utf-8')):
            if link.startswith(('https://', 'http://')):
                if not args.site_only or urlsplit(link).hostname == 'china-revealed.com':
                    urls.add(urldefrag(link)[0])
            elif not args.site_only:
                path, fragment = urldefrag(link)
                target = (source.parent / unquote(path)).resolve() if path else source
                ok = target.is_file() and (not fragment or unquote(fragment) in headings(target.read_text(encoding='utf-8')))
                local.append({'source': name, 'url': link, 'ok': ok})
    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for row in pool.map(check_http, sorted(urls)):
            results.append(row)
            print(f"{'OK' if row['ok'] else 'REVIEW'} {row.get('status', 'ERR')} {row['url']}", flush=True)
    failures = [row for row in results + local if not row['ok']]
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'http_count': len(results),
              'local_count': len(local), 'failure_count': len(failures), 'http': results, 'local': local}
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Checked {len(results)} HTTP URLs and {len(local)} local links; {len(failures)} need review.")
    for row in failures:
        print(json.dumps(row, ensure_ascii=True))
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
