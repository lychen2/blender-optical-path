"""Compose 2D labels over the clean Blender render; no scene text objects.
python examples/annotate_reference.py /render/output /new/annotated.svg
Render the SVG to PNG using Inkscape or: rsvg-convert annotated.svg -o annotated.png
"""
import argparse
import base64
from html import escape
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('render_dir',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--raster',type=Path,help='Optional clean PNG/WebP to embed instead of clean.png')
    args=p.parse_args()
    if args.output.exists():raise FileExistsError('Use a new SVG output path')
    meta=json.loads((args.render_dir/'layout.json').read_text())
    image=args.raster or args.render_dir/'clean.png'
    raster=base64.b64encode(image.read_bytes()).decode()
    mime='image/webp' if image.suffix.lower()=='.webp' else 'image/png'
    width,height=meta.get('image_size',[2100,1050])
    floating=meta['mode']=='floating_optics'
    ink='#e9eef5' if meta.get('style')=='soft-lab' else '#202a34'
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<title>Dual-wavelength optical layout with three positive-positive 4f pairs</title>',
         '<desc>Reference-inspired apparatus with 647 and 485 nm channels, dichroic combining, two supported objective arms and a camera. Nominal layout, not a verified optical prescription.</desc>',
         f'<image width="{width}" height="{height}" xlink:href="data:{mime};base64,{raster}"/>',
         f'<g font-family="DejaVu Sans,Arial,sans-serif" fill="{ink}">']
    # Hand-tuned label positions are in image pixels, independent of 3D geometry.
    labels={
        '647 nm source':(290,98),'485 nm source':(178,255),'M1':(438,435),
        'DM':(463,110),'L1':(583,171),'L2':(708,198),'P':(830,222),
        'NPBS1':(969,245),'Objective 1':(1249,270),'L3':(1415,350),'M3':(1606,343),
        'M2':(743,597),'Specimen':(929,456),'Objective 2':(1117,485),'L4':(1289,524),
        'NPBS2':(1508,826),'Color CMOS camera':(1825,581),'Image plane':(1699,897)}
    if floating:
        offsets={'647 nm source':(0,-62),'485 nm source':(0,66),'M1':(0,93),
                 'DM':(0,-87),'L1':(0,-83),'L2':(0,-83),'P':(0,-70),
                 'NPBS1':(0,-100),'Objective 1':(-45,-68),'L3':(0,-78),'M3':(0,-73),
                 'M2':(-30,83),'Specimen':(-10,205),'Objective 2':(-35,75),'L4':(0,94),
                 'NPBS2':(-10,115),'Color CMOS camera':(-5,-155),'Image plane':(-20,-85)}
        labels={name:(meta['anchors_px'][name][0]+dx,meta['anchors_px'][name][1]+dy)
                for name,(dx,dy) in offsets.items()}
    for name,(x,y) in labels.items():
        tx,ty=meta['anchors_px'][name]
        # Leaders stop short of the optics to preserve the beam path.
        starty=y+9 if ty>y else y-25
        if not floating:
            svg.append(f'<path d="M{x} {starty} L{tx:.1f} {ty-14:.1f}" stroke="#596570" stroke-width="1.4" fill="none" opacity=".8"/>')
        svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="27" font-weight="500">{escape(name)}</text>')
    ix,iy=meta['anchors_px']['Image plane']
    svg.append(f'<path d="M{ix-6} {iy+24} L{ix+6} {iy-24}" stroke="{ink}" stroke-width="2" stroke-dasharray="5 4"/>')
    # Labels and z marker are separate 2D artwork. z is intentionally unnumbered.
    cx,cy=meta['anchors_px']['Color CMOS camera']
    svg.append(f'<path d="M{ix} {iy+59} v12 M{ix} {iy+65} L{cx-20} {cy+65} M{cx-20} {cy+59} v12" stroke="{ink}" stroke-width="1.5"/>')
    svg.append(f'<text x="{(ix+cx-20)/2}" y="{(iy+cy)/2+90}" text-anchor="middle" font-size="25">z</text>')
    svg.append('</g></svg>')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text('\n'.join(svg)+'\n')
    print(args.output)

if __name__=='__main__':main()
