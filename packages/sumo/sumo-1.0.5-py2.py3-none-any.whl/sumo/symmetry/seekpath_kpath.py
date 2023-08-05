# coding: utf-8
# Copyright (c) Scanlon Materials Theory Group
# Distributed under the terms of the MIT License.

"""
Module containing class for generating k-points along paths from SeeK-path.
"""

from sumo.symmetry import Kpath
from itertools import chain


class SeekpathKpath(Kpath):
    r"""Class to generate k-points along paths from SeeK-path.

    More detail on the paths generated by SeeK-path can be found in
    reference [seek]_.

    .. [seek] Y. Hinuma, G. Pizzi, Y. Kumagai, F. Oba, I. Tanaka, Band
              structure diagram paths based on crystallography, Comp. Mat. Sci.
              128, 140 (2017). doi: 10.1016/j.commatsci.2016.10.015

    These paths should be used with primitive structures that comply with the
    definition from the paper. This structure can be accessed using the
    ``prim`` attribute and compliance between the provided structure and
    standardised structure checked using the ``correct_structure()`` method.

    Args:
        structure (:obj:`~pymatgen.core.structure.Structure`): The structure.
        symprec (:obj:`float`, optional): The tolerance for determining the
            crystal symmetry.

    Attributes:
        prim (:obj:`~pymatgen.core.structure.Structure`): The standardised
            primitive cell structure for the generated k-point path.
        conv (:obj:`~pymatgen.core.structure.Structure`): The standardised
            conventional cell structure.

    """

    def __init__(self, structure, symprec=1e-3):
        Kpath.__init__(self, structure, symprec=symprec)

        self._kpath = self.kpath_from_seekpath(self._seek_data['path'],
                                               self._seek_data['point_coords'])

    @classmethod
    def kpath_from_seekpath(cls, seekpath, point_coords):
        r"""Convert seekpath-formatted kpoints path to sumo-preferred format.

        If 'GAMMA' is used as a label this will be replaced by '\Gamma'.

        Args:
            seekpath (list): A :obj:`list` of 2-tuples containing the labels at
                each side of each segment of the k-point path::

                    [(A, B), (B, C), (C, D), ...]

                where a break in the sequence is indicated by a non-repeating
                label. E.g.::

                    [(A, B), (B, C), (D, E), ...]

                for a break between C and D.
            point_coords (dict): Dict of coordinates corresponding to k-point
                labels::

                    {'GAMMA': [0., 0., 0.], ...}
        Returns:
            dict: The path and k-points as::

                {
                    'path', [[l1, l2, l3], [l4, l5], ...],
                    'kpoints', {l1: [a1, b1, c1], l2: [a2, b2, c2], ...}
                }
        """
        # convert from seekpath format e.g. [(l1, l2), (l2, l3), (l4, l5)]
        # to our preferred representation [[l1, l2, l3], [l4, l5]]
        path = [[seekpath[0][0]]]
        for (k1, k2) in seekpath:
            if path[-1] and path[-1][-1] == k1:
                path[-1].append(k2)
            else:
                path.append([k1, k2])

        # Rebuild kpoints dictionary skipping any positions not on path
        # (chain(*list) flattens nested list; set() removes duplicates.)
        kpoints = {p: point_coords[p] for p in set(chain(*path))}

        # Every path should include Gamma-point. Change the label to \Gamma
        assert 'GAMMA' in kpoints
        kpoints[r'\Gamma'] = kpoints.pop('GAMMA')
        path = [[label.replace('GAMMA', r'\Gamma') for label in subpath]
                for subpath in path]

        return {'kpoints': kpoints, 'path': path}
