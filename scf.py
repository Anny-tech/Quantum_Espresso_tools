#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:39:16 2022

@author: ankita_b
"""
import os
import numpy as np
import shutil
import subprocess
from collections import OrderedDict
from subprocess import call
import pandas as pd
import re
import itertools
import sys
import operator
import time


import requests
import os
import zipfile
import tempfile
import argparse

with open('file_name_ID.txt', 'r') as read_obj:
     lines = [line.strip() for line in read_obj]
file_name_ID = lines[0]

indices= []
with open('relax_'+file_name_ID+'.out', 'r') as read_obj:
     lines = [line.strip() for line in read_obj]
for i in range(len(lines)):
    if 'ATOMIC_POSITIONS (crystal)' in lines[i]:
         indices.append(i)
pos = lines[indices[-1]+1:indices[-1]+41]

slurm_param = {'-t ': '24:00:00', '-N ': '4', '--ntasks-per-node=': '20', '-p ': 'parallel', '-A ': 'migroup'}
#slurm_param = {'--time=':'2:00:00', '-p ':'gpu', '--gres=gpu:':'2', '--mem=':'40G','-C ': 'v100|a100'}

scf_control = {'calculation' : "'scf'", 'pseudo_dir' : "'/home/ab8ky/PSEUDO/'",
               'outdir' : "'/scratch/ab8ky/TEMP/'", 'prefix' : "'struc_"+file_name_ID+"_scf'",
               'verbosity' : "'high'" , 'restart_mode' : "'from_scratch'",
               'tprnfor' : '.true.', 'tstress' : '.true.' ,'max_seconds' : '7100' }
scf_system = {'ibrav' : '0' , 'celldm(1)' : '0' , 'nat' :  '40' ,
               'ntyp' : '3' , 'ecutwfc' : '60' , 'ecutrho' : '240',
               'occupations' : "'smearing'" , 'smearing' : "'mv'",
               'degauss' : '0.0015'}
scf_electrons = {'diagonalization' : "'david'", 'mixing_mode' : "'plain'",
                 'mixing_beta' : '0.3' , 'conv_thr' : '7.0D-10',
                 'electron_maxstep' : '500'}
scf_ions = {'ion_dynamics' : "'bfgs'"}
scf_cell = {'cell_dynamics' : "'bfgs'", 'press' : '0.0D0' ,
            'cell_dofree' : "'all'", 'press_conv_thr' : '0.1D0'}
pseudo = [( 'Bi', '1.', 'Bi_ONCV_PBE-1.2.upf'), ('Te', '1.', 'Te_ONCV_PBE-1.2.upf'), ('Se', '1.', 'Se_ONCV_PBE-1.2.upf')]
cell_params = [(20.7319107056, 0.0000000000, 0.0000000000), (18.9164073803, 8.4842002172, 0.0000000000), (18.9164073803, 4.0478536128, 7.4563083664)]
kpts = [(4,4,4), (0,0,0)]
with open('scf_'+file_name_ID+'.slurm', 'xt+') as read_obj:
     read_obj.write('#!/bin/bash' + '\n')
     for K, V in slurm_param.items():
         read_obj.write('#SBATCH  ' + K + V + "\n")
     read_obj.write('\n')
     read_obj.write('module load intel/18.0' + '\n')
     read_obj.write('module load intelmpi/18.0' + '\n')
     read_obj.write('module load quantumespresso/6.4.1'+'\n')
     read_obj.write('\n')
     read_obj.write('cat > struc_'+file_name_ID+'_scf.in << EOF' + '\n')
     read_obj.write('&control' + '\n')
     for K, V in scf_control.items():
         read_obj.write('    ' + K + "\t" + "= " + V + " ," + "\n")
     read_obj.write(' /' + '\n')
     read_obj.write(' &system' + '\n')
     for K, V in scf_system.items():
         read_obj.write('    ' + K + "\t" + "= " + V + " ," + "\n")
     read_obj.write(' /' + '\n')
     read_obj.write(' &electrons' + '\n')
     for K, V in scf_electrons.items():
         read_obj.write('    ' + K + "\t" + "= " + V + " ," + "\n")
     read_obj.write(' /' + '\n')
     read_obj.write(' &ions' + '\n')
     for K, V in scf_ions.items():
         read_obj.write('    ' + K + "\t" + "= " + V + " ," + "\n")
     read_obj.write(' /' + '\n')
     read_obj.write(' &cell' + '\n')
     for K, V in scf_cell.items():
         read_obj.write('    ' + K + "\t" + "= " + V + " ," + "\n")
     read_obj.write(' /' + '\n')
     read_obj.write('ATOMIC_SPECIES' + '\n')
     read_obj.write(''.join('{}  {}  {} \n'.format(x[0],x[1],x[2]) for x in pseudo))
     read_obj.write('\n')
     read_obj.write('CELL_PARAMETERS (angstrom)' + '\n')
     read_obj.write(''.join('{}  {}  {} \n'.format(x[0],x[1],x[2]) for x in cell_params))
     read_obj.write('\n')
     read_obj.write('ATOMIC_POSITIONS (crystal)' + '\n')
     for i in pos:
         read_obj.write(i + '\n')
     read_obj.write('\n')
     read_obj.write('K_POINTS automatic' + '\n')
     read_obj.write(' '.join('{} {} {}'.format(x[0],x[1],x[2]) for x in kpts))
     read_obj.write('\n')
     read_obj.write('EOF' + '\n' + 'srun pw.x  < struc_'+file_name_ID+'_scf.in > struc_'+file_name_ID+'_scf.out')
     read_obj.close()
