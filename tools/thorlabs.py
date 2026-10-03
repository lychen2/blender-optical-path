"""Search bundled metadata, download official CAD, convert STEP, clean reviewed faces.
Normal Python; convert/clean require build123d (not Blender's bundled Python).
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import time
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

PACKAGE = Path(__file__).resolve().parents[1]
API = 'https://www.thorlabs.com/graphql'


def official_url(url):
    parsed = urlparse(url)
    host = parsed.hostname or ''
    domains = ('thorlabs.com', 'thorlabschina.cn', 'thorlabscms.cn')
    if parsed.scheme != 'https' or not any(host == d or host.endswith('.' + d) for d in domains):
        raise ValueError(f'Expected official HTTPS Thorlabs URL: {url}')
    return url


class OfficialRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        official_url(newurl)
        if code in (307, 308):
            return Request(newurl, data=req.data, headers=dict(req.headers), method=req.get_method())
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(url, payload=None):
    official_url(url)
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {'User-Agent': 'Optical-components-library/1.0', 'Content-Type': 'application/json',
               'GraphQL-Require-Preflight': '1'}
    for attempt in range(3):
        try:
            with build_opener(OfficialRedirect()).open(Request(url, data=data, headers=headers), timeout=45) as response:
                official_url(response.url)
                return response.read()
        except HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == 2:
                raise
            delay = error.headers.get('Retry-After', str(2 ** attempt))
            # Long retry delays should be retried by the caller, never ignored.
            if not delay.isdigit() or int(delay) > 30:
                raise RuntimeError(f'Server requested retry after {delay}; retry later') from error
            time.sleep(int(delay))


def query(document):
    result = json.loads(request(API, {'query': document}))
    if result.get('errors'):
        raise RuntimeError(json.dumps(result['errors']))
    return result['data']


def download(sku, output):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/_-]{0,100}', sku):
        raise ValueError('Invalid exact SKU')
    store = query('{store(domain:"www.thorlabs.com"){storeId catalogId}}')['store']
    q = json.dumps
    match = query('{validateProduct(sku:' + q(sku) + ',catalogId:' + q(store['catalogId']) +
                  ',currencyCode:"USD",currentLanguage:"en-US"){id sku isValid}}')['validateProduct']
    if not match.get('id') or not match.get('isValid') or match.get('sku', '').casefold() != sku.casefold():
        raise ValueError(f'Exact SKU not found: {sku}')
    product = query('{product(storeId:' + q(store['storeId']) + ',id:' + q(match['id']) +
                    ',currencyCode:"USD",cultureName:"en-US"){id code name assets{id name url group optiUrl}}}')['product']
    folder = output.resolve() / sku.replace('/', '_')
    if folder.exists():
        raise FileExistsError(f'{folder} exists; use a new output directory to preserve originals')
    selected = [a for a in product['assets'] if a['group'] in ('Step', 'CAD PDF')]
    if not any(a['group'] == 'Step' for a in selected):
        raise ValueError(f'No official STEP for {sku}; do not substitute a different model silently')
    # Fetch and verify content before writing the directory.
    files = []
    for asset in selected:
        filename = asset['name']
        if Path(filename).name != filename or filename in ('.', '..'):
            raise ValueError('Invalid downloaded filename')
        url = official_url(asset.get('optiUrl') or asset['url'])
        content = request(url)
        signature = b'ISO-10303' if asset['group'] == 'Step' else b'%PDF'
        if not content.lstrip().startswith(signature):
            raise ValueError(f'Unexpected {asset["group"]} content: {url}')
        files.append((filename, content, url, asset['group']))
    if len({f[0] for f in files}) != len(files):
        raise ValueError('Duplicate source filenames; inspect product assets before downloading')
    folder.mkdir(parents=True)
    records = []
    for name, content, url, kind in files:
        (folder / name).write_bytes(content)
        records.append({'path': name, 'url': url, 'kind': kind,
                        'sha256': hashlib.sha256(content).hexdigest()})
    product['downloaded'] = records
    product['retrieved_utc'] = datetime.now(timezone.utc).isoformat()
    (folder / 'source.json').write_text(json.dumps(product, indent=2) + '\n')
    return {'folder': str(folder), 'sku': product['code'], 'files': len(records)}


def convert(source, output, sku, tolerance=.06):
    from build123d import import_step
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('Tessellation tolerance must be positive, in mm')
    if output.exists():
        raise FileExistsError(output)
    shape = import_step(source)
    if not shape.is_valid:
        raise ValueError('STEP BRep is invalid; inspect before conversion')
    parts = list(shape.solids()) or list(shape.shells())
    if not parts:
        raise ValueError('No solids or shells to tessellate')
    solids = []
    for solid in parts:
        vertices, faces = solid.tessellate(tolerance, .16)
        solids.append({'vertices': [[v.X, v.Y, v.Z] for v in vertices], 'faces': faces})
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    cleanup_path = source.with_suffix('.cleanup.json')
    cleanup = json.loads(cleanup_path.read_text()) if cleanup_path.exists() else None
    if cleanup and cleanup.get('output_sha256') != digest:
        raise ValueError('Cleanup report hash does not match STEP')
    result = {'sku': sku, 'source': source.name, 'source_sha256': digest,
              'units': 'mm', 'tolerance_mm': tolerance, 'solids': solids,
              'lettering_removed': bool(cleanup), 'cleanup_report': cleanup,
              'bounds': [list(shape.bounding_box().min), list(shape.bounding_box().max)]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output, 'wt') as stream:
        json.dump(result, stream)
    return {'output': str(output), 'parts': len(parts), 'triangles': sum(len(s['faces']) for s in solids)}


def clean(source, rules_path, output):
    """Only hash-bound, manually inspected solid-face rules are accepted.
    Shell sources need a separately reviewed face-replacement procedure.
    """
    from build123d import import_step, Solid, Compound, export_step
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Defeaturing
    rules = json.loads(rules_path.read_text())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if rules['source_sha256'] != digest:
        raise ValueError('STEP hash differs from inspected cleanup rules; re-inspect face indices')
    if output.exists() or output.resolve() == source.resolve():
        raise FileExistsError('Cleanup output must be a new derivative file')
    shape = import_step(source)
    solids = list(shape.solids())
    if len(solids) != rules['solid_count'] or len(shape.shells()) != len(solids):
        raise ValueError('Source has unexpected solid/shell structure; use a reviewed shell workflow')
    cleaned, changes = [], []
    mappings = {int(k): v for k, v in rules['solids'].items()}
    if not mappings or any(i < 0 or i >= len(solids) for i in mappings):
        raise ValueError('Cleanup rules need valid, inspected solid indices')
    for i, solid in enumerate(solids):
        if i not in mappings:
            cleaned.append(solid)
            continue
        rule = mappings[i]
        faces = list(solid.faces())
        if len(faces) != rule['face_count']:
            raise ValueError(f'Face count changed for solid {i}')
        indices = rule['remove_faces']
        if not indices or len(set(indices)) != len(indices) or any(type(j) is not int or j < 0 or j >= len(faces) for j in indices):
            raise ValueError('Invalid inspected face index list')
        tool = BRepAlgoAPI_Defeaturing()
        tool.SetShape(solid.wrapped)
        for j in indices:
            tool.AddFaceToRemove(faces[j].wrapped)
        tool.Build()
        if not tool.IsDone():
            raise ValueError(f'Defeaturing failed for solid {i}')
        result = Solid(tool.Shape())
        delta = result.volume - solid.volume
        before, after = solid.bounding_box(), result.bounding_box()
        bounds_delta = max(abs(a-b) for a, b in zip([*before.min, *before.max], [*after.min, *after.max]))
        if not result.is_valid or not -.01 <= delta <= rule['max_volume_added_mm3'] or bounds_delta > .001:
            raise ValueError(f'Cleanup changed structural geometry for solid {i}: volume={delta}, bounds={bounds_delta}')
        cleaned.append(result)
        changes.append({'solid': i, 'removed_faces': indices, 'volume_added_mm3': delta,
                        'bounds_max_delta_mm': bounds_delta, 'valid': True})
    output.parent.mkdir(parents=True, exist_ok=True)
    export_step(Compound(children=cleaned), output)
    report = {'source_sha256': digest, 'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'rules': rules, 'changes': changes}
    output.with_suffix('.cleanup.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    search = sub.add_parser('search'); search.add_argument('query', nargs='?', default='')
    dl = sub.add_parser('download'); dl.add_argument('sku'); dl.add_argument('--output', type=Path, required=True)
    cv = sub.add_parser('convert'); cv.add_argument('source', type=Path); cv.add_argument('--output', type=Path, required=True)
    cv.add_argument('--sku', required=True); cv.add_argument('--tolerance', type=float, default=.06)
    cl = sub.add_parser('clean'); cl.add_argument('source', type=Path); cl.add_argument('--rules', type=Path, required=True)
    cl.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'search':
        rows = json.loads((PACKAGE / 'library/index.json').read_text())['assets']
        result = [r for r in rows if args.query.casefold() in json.dumps(r).casefold()]
    elif args.action == 'download': result = download(args.sku, args.output)
    elif args.action == 'convert': result = convert(args.source, args.output, args.sku, args.tolerance)
    else: result = clean(args.source, args.rules, args.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
