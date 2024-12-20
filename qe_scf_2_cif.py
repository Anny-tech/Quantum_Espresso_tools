#!/usr/bin/env python
# coding: utf-8


from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter


def qe_input_to_cif(input_file_path, output_cif_path):
    """
    Converts a Quantum Espresso SCF input file to a .cif file using pymatgen.

    Parameters:
        input_file_path (str): Path to the Quantum Espresso SCF input file.
        output_cif_path (str): Path where the .cif file will be saved.

    Returns:
        None: Saves the .cif file to the specified output path.
    """
    try:
        # Read input file
        with open(input_file_path, 'r') as file:
            lines = file.readlines()

        # Extract number of atoms
        n_atom_line = next(line for line in lines if line.strip().startswith("nat ="))
        n_atom = int(n_atom_line.split('=')[1].strip().strip(','))

        # Extract 'CELL_PARAMETERS'
        cell_start = next(i for i, line in enumerate(lines) if line.strip().startswith("CELL_PARAMETERS"))
        lattice_parameters = [list(map(float, lines[cell_start + i].split())) for i in range(1, 4)]

        # Extract 'ATOMIC_POSITIONS'
        atomic_start = next(i for i, line in enumerate(lines) if line.strip().startswith("ATOMIC_POSITIONS"))
        atomic_positions = [line.split() for line in lines[atomic_start + 1:atomic_start + 1 + n_atom]]

        # Prepare atomic coordinates for Pymatgen
        atomic_sites = [(pos[0], list(map(float, pos[1:]))) for pos in atomic_positions]

        # Create structure object using Pymatgen
        structure = Structure(lattice_parameters, [site[0] for site in atomic_sites], [site[1] for site in atomic_sites])

        # Save structure to a .cif file
        structure.to(filename=output_cif_path)
        print(f"Structure successfully saved to {output_cif_path}")

    except Exception as e:
        print(f"Error occurred: {e}")



