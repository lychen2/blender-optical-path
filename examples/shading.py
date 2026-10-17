"""Compatibility entry for the shared optical-figure presets."""
import runpy
from pathlib import Path

_shared = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'tools/styles.py'))
STYLES = _shared['STYLES']
apply_style = _shared['apply_style']
