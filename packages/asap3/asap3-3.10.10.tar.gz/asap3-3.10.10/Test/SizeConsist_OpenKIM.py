from __future__ import print_function
from asap3 import *
from numpy import *
from asap3.testtools import ReportTest
from ase.lattice.cubic import *
from OpenKIM_modelname import openkimmodel

element = 'Au'
if OpenKIMsupported:
    sizes = arange(10,0,-1)
    pbc_candidates = ["NEIGH_RVEC_H", 
                      "NEIGH_PURE_H",
                      "NEIGH_RVEC_F", 
                      "NEIGH_PURE_F",
                      ]
else:
    sizes = []
    pbc_candidates = []

energy = None
force = None

for nbl in pbc_candidates:
    for s in sizes:
        atoms = FaceCenteredCubic(symbol=element, size=(s,s,s), pbc=True)
        r = atoms.get_positions()
        for i in range(0, len(r), 4):
            r[i][0] += 0.1
        atoms.set_positions(r)
        atoms.set_calculator(OpenKIMcalculator(openkimmodel, allowed=nbl))
        e = atoms.get_potential_energy() / len(atoms)   
        print("%5i atoms: E = %.5f eV/atom" % (len(atoms), e))
        if energy is None:
            energy = e
        else:
            ReportTest("Energy for size %i (%i atoms)" % (s, len(atoms)),
                       e, energy, 1e-8)
        f = atoms.get_forces()
        if force is None:
            force = f[:4]
        else:
            for i in range(len(f)):
                for j in range(3):
                    ReportTest("Force for size %i atom %i of %i component %i"
                               % (s, i, len(atoms), j),
                               f[i,j], force[i % 4, j], 1e-8, silent=True)
            #print force
            #print f[:10]
        del atoms

ReportTest.Summary()
