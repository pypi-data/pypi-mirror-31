# coding: utf-8
# Copyright (c) Scanlon Materials Theory Group
# Distributed under the terms of the MIT License.

"""
Module containing class for generating k-points along paths from pymatgen.
"""

from sumo.symmetry import Kpath

from pymatgen.symmetry.bandstructure import HighSymmKpath


class PymatgenKpath(Kpath):
    r"""Class to generate k-points along paths from pymatgen.

    More detail on the paths generated by can be found in the pymatgen
    documentation. These paths are based on the work described in reference
    [curt]_.

    .. [curt] Setyawan, W., & Curtarolo, S. High-throughput electronic band
              structure calculations: Challenges and tools, Computational
              Materials Science, 49, 299-312 (2010). doi:
              10.1016/j.commatsci.2010.05.010

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
        pmg_path = HighSymmKpath(structure, symprec=symprec)
        self._kpath = pmg_path._kpath
        self.prim = pmg_path.prim
        self.conv = pmg_path.conventional
