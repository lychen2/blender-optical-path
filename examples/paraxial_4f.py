"""Normalized paraxial 4f checks for the illumination-envelope example.
Model length units are arbitrary; they are NOT the CAD scene millimetres.
Run with ordinary Python to verify all three lens pairs before rendering.
"""
import math


def propagate(ray, distance):
    h, theta = ray
    return h + distance * theta, theta


def lens(ray, focal_length):
    h, theta = ray
    return h, theta - h / focal_length


def pair(name, f1, f2, h=.04):
    assert f1 > 0 and f2 > 0
    incoming = (h, 0.)
    after_first = lens(incoming, f1)
    at_focus = propagate(after_first, f1)
    before_second = propagate(at_focus, f2)
    outgoing = lens(before_second, f2)
    assert abs(at_focus[0]) < 1e-12
    assert abs(outgoing[1]) < 1e-12
    assert math.isclose(outgoing[0] / h, -f2 / f1)
    # Object-plane ray basis verifies a plane-to-plane relay independently
    # of the illumination bundle drawn in the scene.
    def relay(ray):
        return propagate(lens(propagate(lens(propagate(ray, f1), f1), f1+f2), f2), f2)
    col0, col1 = relay((1., 0.)), relay((0., 1.))
    assert abs(col1[0]) < 1e-12  # B=0: conjugate planes
    assert abs(col0[0]+f2/f1)<1e-12
    return {'name':name,'f1':f1,'f2':f2,'units':'normalized, not mm',
            'object_plane':-f1,'first_lens':0,'shared_focus':f1,
            'second_lens':f1+f2,'image_plane':f1+2*f2,
            'checkpoints':{'input':incoming,'after_first':after_first,'focus':at_focus,
                           'before_second':before_second,'output':outgoing},
            'relay_matrix':[[col0[0],col1[0]],[col0[1],col1[1]]],
            'diameter_ratio':f2/f1,'signed_magnification':-f2/f1}


def prescription():
    return {'model':'Thin positive lenses, paraxial geometrical illumination envelope',
            'assumptions':['User-approved symbolic relations and illustrative ratios.',
                'L1/L2 ratio 1:2; objective/relay-lens pairs shown 1:1 for readability.',
                'RMS10X housing is manufacturer geometry, not an internal optical prescription.',
                'Both wavelengths share ideal achromatic powers; no chromatic aberration model.',
                'Same-axis recombination; camera z offset is illustrative, no carrier/fringe simulation.',
                'A positive display radius floor is a drawing aid, not a calculated diffraction waist.'],
            'pairs':[pair('L1 / L2',1.,2.),pair('Objective 1 / L3',1.,1.),pair('Objective 2 / L4',1.,1.)]}

if __name__=='__main__':
    import json
    print(json.dumps(prescription(),indent=2))
