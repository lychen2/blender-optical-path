"""Executable textbook acceptance checks for the dependency-free optics model."""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import optical_model as optics


def close(actual, expected, *, rel=1e-10, abs_=1e-12):
    assert math.isclose(actual, expected, rel_tol=rel, abs_tol=abs_), (actual, expected)


def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('invalid input was accepted')


# Textbook free-space Gaussian: z_R=pi*w0^2/lambda and w(z_R)=sqrt(2)*w0.
# Independently calculated for lambda=500 nm and w0=0.1 mm.
wavelength_nm = 500.0
waist_mm = 0.1
rayleigh_mm = math.pi * 0.1 ** 2 / 0.0005
assert math.isclose(rayleigh_mm, 62.83185307179586, rel_tol=1e-14)
free = optics.gaussian_beam(wavelength_nm, waist_mm, 0.0, [], rayleigh_mm, samples=3)
assert set(free) == {'samples', 'checkpoints', 'model_scope'}
assert len(free['samples']) == 3 and free['checkpoints'] == []
for sample in free['samples']:
    assert set(sample) == {'position_mm', 'radius_mm', 'curvature_mm', 'gouy_rad'}
close(free['samples'][0]['radius_mm'], 0.1)
assert free['samples'][0]['curvature_mm'] is None
close(free['samples'][1]['radius_mm'], 0.1 * math.sqrt(1.25))
close(free['samples'][2]['radius_mm'], 0.1 * math.sqrt(2.0))
close(free['samples'][2]['curvature_mm'], 2.0 * rayleigh_mm)
close(free['samples'][2]['gouy_rad'], math.pi / 4)

# A thin lens leaves spot radius continuous but alters wavefront curvature.
f = 100.0
lens = [{'position_mm': 0.0, 'focal_length_mm': f}]
through_lens = optics.gaussian_beam(wavelength_nm, waist_mm, 0.0, lens, 20.0, samples=3)
checkpoint = through_lens['checkpoints'][0]
close(checkpoint['before']['radius_mm'], checkpoint['after']['radius_mm'])
assert checkpoint['before']['curvature_mm'] is None  # plane wavefront at the waist
assert checkpoint['after']['curvature_mm'] is not None
assert checkpoint['after']['curvature_mm'] != checkpoint['before']['curvature_mm']
assert all(isinstance(x, (int, float, type(None))) for row in through_lens['samples']
           for x in row.values())
json.dumps(through_lens, allow_nan=False)

# Textbook 4f relay with input/output focal planes: diag(-f2/f1,-f1/f2).
f1, f2 = 50.0, 100.0
relay = [{'position_mm': 50.0, 'focal_length_mm': f1},
         {'position_mm': 200.0, 'focal_length_mm': f2}]
expected = [[-2.0, 0.0], [0.0, -0.5]]
actual = optics.abcd_system(relay, 0.0, 300.0)
for row, exp_row in zip(actual, expected):
    for value, exp in zip(row, exp_row):
        close(value, exp, abs_=1e-12)
ray = optics.trace_paraxial_ray(1.0, 0.0, relay, 0.0, 300.0)
assert any(row['side'] == 'before' and row['position_mm'] == 50.0 for row in ray)
assert any(row['side'] == 'after' and row['position_mm'] == 50.0 for row in ray)
close(ray[-1]['height_mm'], -2.0)
close(ray[-1]['angle_rad'], 0.0)

# Jones convention: QWP at 45 degrees maps horizontal to equal quadrature;
# HWP at 45 degrees rotates horizontal linear polarization to vertical.
h = (1 + 0j, 0j)
qwp = optics.waveplate(h, math.pi / 2, 45.0)
assert math.isclose(abs(qwp[0]), 1 / math.sqrt(2), rel_tol=1e-12)
assert math.isclose(abs(qwp[1]), 1 / math.sqrt(2), rel_tol=1e-12)
assert abs((qwp[1] / qwp[0]).imag) > 0.999999999
hwp = optics.waveplate(h, math.pi, 45.0)
close(abs(hwp[0]), 0.0)
close(abs(hwp[1]), 1.0)
projected = optics.polarizer((1 + 0j, 1 + 0j), 0.0)
assert projected == (1 + 0j, 0j)
assert optics.stokes((1 + 0j, 0j)) == [1.0, 1.0, 0.0, 0.0]

# Normal-incidence air/glass: R=((1.5-1)/(1.5+1))^2=0.04, T=0.96.
normal = optics.fresnel(1.0, 1.5, 0.0)
close(normal['Rs'], 0.04)
close(normal['Rp'], 0.04)
close(normal['Ts'], 0.96)
close(normal['Tp'], 0.96)
assert normal['tir'] is False
# Glass-to-air incidence beyond asin(1/1.5) is total internal reflection.
tir = optics.fresnel(1.5, 1.0, 50.0)
assert tir == {'Rs': 1.0, 'Rp': 1.0, 'Ts': 0.0, 'Tp': 0.0, 'tir': True}

# Inputs are rejected rather than silently sorted, clipped, or propagated.
expect_value_error(lambda: optics.gaussian_beam(500, 0.1, 0, [], 0, samples=1))
expect_value_error(lambda: optics.gaussian_beam(float('nan'), 0.1, 0, [], 10))
expect_value_error(lambda: optics.abcd_system([], 2, 1))
expect_value_error(lambda: optics.abcd_system([
    {'position_mm': 3, 'focal_length_mm': 1},
    {'position_mm': 2, 'focal_length_mm': 1}], 0, 4))
expect_value_error(lambda: optics.trace_paraxial_ray(1, 0, [], 2, 1))
expect_value_error(lambda: optics.fresnel(1, 1.5, 91))

print('OPTICAL_MODEL_CHECK_PASSED')
print('Independent expectations: zR={:.12f} mm; w(zR)={:.12f} mm; 4f ABCD={}'.format(
    rayleigh_mm, waist_mm * math.sqrt(2), expected))
