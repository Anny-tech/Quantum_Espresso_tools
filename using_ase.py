#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:39:16 2022

@author: shunl
"""
from os import listdir, mkdir
from os.path import isdir
from ase.io import read, write
import numpy as np
import pandas as pd


def composition_name(count_of_new_chemical):
    dictlist = []
    for key, value in count_of_new_chemical.items():
        temp = [key,value]
        dictlist.append(temp)
    dictlist = list(np.concatenate(dictlist).flat)
    return dictlist

all_temp_files = listdir('./temp/')


composition_new_candidates = [['Al','Mo','Nb','Ti','V'],
                   ['Al','Nb','Ta','Ti','V'],
                   ['Hf','Mo','Nb','Ta','Ti'],
                   ['Hf','Mo','Nb','Ta','Zr'],
                   ['Hf','Mo','Ta','Ti','Zr'],
                   ['Hf','Mo','Nb','Ti','Zr'],
                   ['Mo','Nb','Ta','Ti','V'],
                   ['Mo','Nb','Ti','V','Zr'],
                   ['Nb','Ta','Ti','V','W']]

for composition_new in composition_new_candidates:
    for file_name in all_temp_files: 
        input1 = read('./temp/{file}'.format(file=file_name), format="espresso-in")
        
        cell = input1.get_cell()
        
        chemical_symbols = input1.get_chemical_symbols()
        
        composition_old = list(dict.fromkeys(chemical_symbols))
        
        new_dir = ''.join(composition_new)
        
        if not isdir(new_dir):
            mkdir(new_dir)
            print('Directory created')
        
        diff_new_to_old = list(set(composition_new) - set(composition_old))
        diff_old_to_new = list(set(composition_old) - set(composition_new))
        diff_array = np.array([diff_old_to_new, diff_new_to_old]).T
        diff_array = diff_array.tolist()
        
        
        replace_dict = dict(diff_array)
        
        chemical_symbols_series = pd.Series(chemical_symbols)
        new_chemical_symbols_series = chemical_symbols_series.replace(replace_dict)
        new_chemical_symbols = new_chemical_symbols_series.tolist()
        
        count_of_new_chemical = new_chemical_symbols_series.value_counts().to_dict()
        
        new_input = input1.copy()
        new_input.set_chemical_symbols(new_chemical_symbols)
        
        
        input_para = {
            'calculation' : 'vc-relax',
            'disk_io ': 'none',
            'verbosity' : 'high',
            'prefix' : '{composition}_vc-relax'.format(composition= ''.join(composition_name(count_of_new_chemical))),
            'outdir' : '/scratch/ejf5wk/TEMP',
            'pseudo_dir' : '/home/ejf5wk/DFT/pp/PBEsol_PSlibrary_1.0.0/',
            'tprnfor' : True,
            'tstress' : True,
            'forc_conv_thr' : '1.0D-4',
            'restart_mode' : 'from_scratch',
            'system':{
                'ecutwfc' : 60.0, 
                'ecutrho' : 731,
                'occupations' : 'smearing',
                'smearing' : 'gauss', 
                'degauss' : 0.02},
            'electrons': {
                'mixing_beta' :0.2,
            'electron_maxstep' : 300}
            }
        
        
        pseudopotentials = {'Mo':'Mo.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'Al':'Al.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'Nb':'Nb.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'Ti':'Ti.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'W':'W.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'V':'V.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'Zr': 'Zr.pbesol-spn-rrkjus_psl.1.0.0.UPF',
                            'Hf': 'Hf.pbesol-spn-rrkjus_psl.1.0.0.UPF'}
        
        
        write("./{new_dir}/{composition}_vc_relax.in".format(composition= ''.join(composition_name(count_of_new_chemical)), new_dir=new_dir),\
              images= new_input,format="espresso-in",kspacing= 0.045,\
              pseudopotentials=pseudopotentials,\
              input_data= input_para)