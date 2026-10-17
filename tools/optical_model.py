"""Dependency-free scalar paraxial optics in homogeneous air.

Scope: exact first-order ABCD propagation for a monochromatic Gaussian beam
and ideal thin lenses, with all longitudinal/transverse coordinates in mm and
wavelength supplied in nm. Ray tracing is paraxial and one-dimensional. Jones
waveplates/polarizers and lossless, isotropic dielectric Fresnel coefficients
are ideal; no coatings, absorption, apertures, aberrations, vector focusing,
nonlinear effects, or measured component prescriptions are modeled. This is
not a Blender (bpy) module.
"""
import math


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('{} must be a finite number'.format(name))
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('{} must be a finite number'.format(name))
    return value


def _positive(value, name):
    value = _number(value, name)
    if value <= 0:
        raise ValueError('{} must be positive'.format(name))
    return value


def _elements(elements, start_mm, end_mm):
    if not isinstance(elements, (list, tuple)):
        raise ValueError('elements must be an ordered list or tuple')
    result = []
    previous = -math.inf
    for i, element in enumerate(elements):
        if not isinstance(element, dict) or 'position_mm' not in element or 'focal_length_mm' not in element:
            raise ValueError('each element must provide position_mm and focal_length_mm')
        position = _number(element['position_mm'], 'elements[{}].position_mm'.format(i))
        focal = _number(element['focal_length_mm'], 'elements[{}].focal_length_mm'.format(i))
        if focal == 0:
            raise ValueError('focal_length_mm must be nonzero')
        if position < previous:
            raise ValueError('elements must be sorted by position_mm')
        if position < start_mm or position > end_mm:
            raise ValueError('element positions must lie within start_mm and end_mm')
        result.append((position, focal))
        previous = position
    return result


def _matmul(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (a * e + b * g, a * f + b * h,
            c * e + d * g, c * f + d * h)


def _system(elements, start_mm, end_mm):
    matrix = (1.0, 0.0, 0.0, 1.0)
    position = start_mm
    for lens_position, focal in elements:
        distance = lens_position - position
        matrix = _matmul((1.0, distance, 0.0, 1.0), matrix)
        matrix = _matmul((1.0, 0.0, -1.0 / focal, 1.0), matrix)
        position = lens_position
    return _matmul((1.0, end_mm - position, 0.0, 1.0), matrix)


def abcd_system(elements, start_mm, end_mm):
    """Return the 2x2 ray-transfer matrix from start_mm through end_mm."""
    start = _number(start_mm, 'start_mm')
    end = _number(end_mm, 'end_mm')
    if end < start:
        raise ValueError('end_mm must not precede start_mm')
    lenses = _elements(elements, start, end)
    a, b, c, d = _system(lenses, start, end)
    return [[a, b], [c, d]]


def _q_lens(q, focal):
    return q / (1.0 - q / focal)


def _beam_values(q, wavelength_mm):
    inverse = 1.0 / q
    radius = math.sqrt(-wavelength_mm / (math.pi * inverse.imag))
    curvature = None if inverse.real == 0.0 else 1.0 / inverse.real
    return {'radius_mm': radius, 'curvature_mm': curvature,
            'gouy_rad': math.atan2(q.real, q.imag)}


def gaussian_beam(wavelength_nm, waist_mm, waist_position_mm, elements, end_mm, samples=81):
    """Calculate an ideal Gaussian beam; samples are post-lens at coincident planes.

    Lens checkpoints contain ``before`` and ``after`` values; radius is
    continuous across each ideal thin lens while curvature can change abruptly.
    A plane wavefront's infinite curvature is represented by JSON-safe None.
    """
    wavelength = _positive(wavelength_nm, 'wavelength_nm') * 1e-6
    waist = _positive(waist_mm, 'waist_mm')
    waist_position = _number(waist_position_mm, 'waist_position_mm')
    end = _number(end_mm, 'end_mm')
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 2:
        raise ValueError('samples must be an integer of at least 2')
    if end < waist_position:
        raise ValueError('end_mm must not precede waist_position_mm')
    lenses = _elements(elements, waist_position, end)
    z_rayleigh = math.pi * waist * waist / wavelength
    start_q = complex(0.0, z_rayleigh)

    # Evaluate q robustly by sequentially propagating from the waist. This also
    # handles an element exactly at the waist coordinate without a zero gap.
    def state_at(position):
        q = start_q
        cursor = waist_position
        for lens_position, focal in lenses:
            if lens_position > position:
                break
            q += lens_position - cursor
            q = _q_lens(q, focal)
            cursor = lens_position
        return q + (position - cursor)

    step = (end - waist_position) / (samples - 1)
    sample_positions = [waist_position + i * step for i in range(samples)]
    output_samples = []
    for position in sample_positions:
        row = {'position_mm': position}
        row.update(_beam_values(state_at(position), wavelength))
        output_samples.append(row)

    checkpoints = []
    for lens_index, (lens_position, focal) in enumerate(lenses):
        q = start_q
        cursor = waist_position
        for earlier_position, earlier_focal in lenses[:lens_index]:
            q += earlier_position - cursor
            q = _q_lens(q, earlier_focal)
            cursor = earlier_position
        q += lens_position - cursor
        q_after = _q_lens(q, focal)
        before = _beam_values(q, wavelength)
        after = _beam_values(q_after, wavelength)
        checkpoints.append({'position_mm': lens_position, 'before': before, 'after': after})

    return {'samples': output_samples, 'checkpoints': checkpoints,
            'model_scope': 'Scalar paraxial Gaussian q; homogeneous air; ideal thin lenses; no aberrations or apertures.'}


def trace_paraxial_ray(height_mm, angle_rad, elements, start_mm, end_mm):
    """Trace a height/angle ray and report each lens plane on both sides."""
    height = _number(height_mm, 'height_mm')
    angle = _number(angle_rad, 'angle_rad')
    start = _number(start_mm, 'start_mm')
    end = _number(end_mm, 'end_mm')
    if end < start:
        raise ValueError('end_mm must not precede start_mm')
    lenses = _elements(elements, start, end)
    checkpoints = [{'position_mm': start, 'side': 'start', 'height_mm': height,
                    'angle_rad': angle}]
    cursor = start
    for position, focal in lenses:
        height += (position - cursor) * angle
        checkpoints.append({'position_mm': position, 'side': 'before',
                            'height_mm': height, 'angle_rad': angle})
        angle -= height / focal
        checkpoints.append({'position_mm': position, 'side': 'after',
                            'height_mm': height, 'angle_rad': angle})
        cursor = position
    height += (end - cursor) * angle
    checkpoints.append({'position_mm': end, 'side': 'end', 'height_mm': height,
                        'angle_rad': angle})
    return checkpoints


def _jones(jones):
    if not isinstance(jones, (list, tuple)) or len(jones) != 2:
        raise ValueError('jones must contain two complex components')
    values = []
    for component in jones:
        try:
            value = complex(component)
        except (TypeError, ValueError, OverflowError):
            raise ValueError('Jones components must be finite complex numbers')
        if not math.isfinite(value.real) or not math.isfinite(value.imag):
            raise ValueError('Jones components must be finite complex numbers')
        values.append(value)
    return values


def _angle(value, name):
    return math.radians(_number(value, name))


def waveplate(jones, retardance_rad, angle_deg):
    """Apply an ideal linear retarder; positive retardance delays the local y axis."""
    x, y = _jones(jones)
    retardance = _number(retardance_rad, 'retardance_rad')
    theta = _angle(angle_deg, 'angle_deg')
    c, s = math.cos(theta), math.sin(theta)
    local_x, local_y = c * x + s * y, -s * x + c * y
    local_y *= complex(math.cos(retardance), math.sin(retardance))
    return (c * local_x - s * local_y, s * local_x + c * local_y)


def polarizer(jones, angle_deg):
    """Project a Jones vector onto an ideal linear transmission axis."""
    x, y = _jones(jones)
    theta = _angle(angle_deg, 'angle_deg')
    c, s = math.cos(theta), math.sin(theta)
    amplitude = c * x + s * y
    return (c * amplitude, s * amplitude)


def stokes(jones):
    """Return normalized-independent [S0,S1,S2,S3], with S3=2 Im(conj(x)*y)."""
    x, y = _jones(jones)
    return [float((abs(x) ** 2 + abs(y) ** 2)),
            float((abs(x) ** 2 - abs(y) ** 2)),
            float(2.0 * (x.conjugate() * y).real),
            float(2.0 * (x.conjugate() * y).imag)]


def fresnel(n1, n2, incidence_deg):
    """Return power Fresnel coefficients Rs/Rp/Ts/Tp for nonmagnetic dielectrics."""
    n1 = _positive(n1, 'n1')
    n2 = _positive(n2, 'n2')
    incidence = _number(incidence_deg, 'incidence_deg')
    if incidence < 0 or incidence > 90:
        raise ValueError('incidence_deg must be in [0, 90]')
    if n1 == n2:
        return {'Rs': 0.0, 'Rp': 0.0, 'Ts': 1.0, 'Tp': 1.0, 'tir': False}
    theta_i = math.radians(incidence)
    sin_t = (n1 / n2) * math.sin(theta_i)
    if sin_t > 1.0:
        return {'Rs': 1.0, 'Rp': 1.0, 'Ts': 0.0, 'Tp': 0.0, 'tir': True}
    theta_t = math.asin(min(1.0, sin_t))
    ci, ct = math.cos(theta_i), math.cos(theta_t)
    rs_den = n1 * ci + n2 * ct
    rp_den = n1 * ct + n2 * ci
    rs = ((n1 * ci - n2 * ct) / rs_den) ** 2
    rp = ((n1 * ct - n2 * ci) / rp_den) ** 2
    return {'Rs': rs, 'Rp': rp, 'Ts': 1.0 - rs, 'Tp': 1.0 - rp, 'tir': False}
