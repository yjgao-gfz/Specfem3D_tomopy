#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# this code could generate the real x y z coordinates for gll points, then you could modify your velocity model easily.
# note that, the first and final points in the orginal binary file is not used for the generation of gll coorinate files e.g. proc000000x_gll_recovered.bin

import numpy as np
import os
databases_mpi_path='DATABASES_MPI'






def recover_gll_coordinates(vp_file, ibool_file, x_file, y_file, z_file, output_dir='DATABASES_MPI', processor_id='000000'):
    # Load the input data
    vp = np.fromfile(vp_file, dtype='float32')
    nspec = (vp.size - 2) // (5 * 5 * 5)  # Calculate nspec based on vp size, excluding first and last points
    vp = vp[1:-1].reshape((nspec, 5, 5, 5))
    
    ibool = np.fromfile(ibool_file, dtype='int32')[1:-1].reshape((nspec, 5, 5, 5))
    x_store = np.fromfile(x_file, dtype='float32')[1:]
    y_store = np.fromfile(y_file, dtype='float32')[1:]
    z_store = np.fromfile(z_file, dtype='float32')[1:]

    # Initialize output arrays with the same shape as vp
    x_gll = np.zeros(vp.shape, dtype='float32')
    y_gll = np.zeros(vp.shape, dtype='float32')
    z_gll = np.zeros(vp.shape, dtype='float32')
    #print(nspec)
    # Iterate over all elements and GLL points to recover global coordinates
    for ispec in range(nspec):
        for i in range(5):
            for j in range(5):
                for k in range(5):
                    iglob = ibool[ispec, i, j, k]-1  # Fortran to Python index conversion
                    #print(iglob)
                    if iglob >= 0:  # Ensure valid index
                        #print(ispec, i, j, k,   z_store[iglob])
                        x_gll[ispec, i, j, k] = x_store[iglob]
                        y_gll[ispec, i, j, k] = y_store[iglob]
                        z_gll[ispec, i, j, k] = z_store[iglob]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write GLL coordinates to binary files
    x_gll.tofile(os.path.join(output_dir, f'proc{processor_id}_x_gll_recovered.bin'))
    y_gll.tofile(os.path.join(output_dir, f'proc{processor_id}_y_gll_recovered.bin'))
    z_gll.tofile(os.path.join(output_dir, f'proc{processor_id}_z_gll_recovered.bin'))

# Example usage for multiple processors:
ncpu=12
for proc_id in range(ncpu):
    print(proc_id)
    processor_id_str = f'{proc_id:06d}'
    recover_gll_coordinates(
        f'DATABASES_MPI/proc{processor_id_str}_vp.bin',
        f'DATABASES_MPI/proc{processor_id_str}_ibool.bin',
        f'DATABASES_MPI/proc{processor_id_str}_x.bin',
        f'DATABASES_MPI/proc{processor_id_str}_y.bin',
        f'DATABASES_MPI/proc{processor_id_str}_z.bin',
        output_dir='DATABASES_MPI',
        processor_id=processor_id_str
    )



def apply_velocity_anomaly(vp_file, x_file, y_file, z_file, output_dir='DATABASES_MPI', processor_id='000000'):
    # Load the input data
    vp = np.fromfile(vp_file, dtype='float32')
    first_element = vp[0]
    last_element = vp[-1]
    nspec = (vp.size - 2) // (5 * 5 * 5)  # Calculate nspec based on vp size, excluding first and last points
    vp = vp[1:-1].reshape((nspec, 5, 5, 5))

    x_gll = np.fromfile(x_file, dtype='float32').reshape((nspec, 5, 5, 5))
    y_gll = np.fromfile(y_file, dtype='float32').reshape((nspec, 5, 5, 5))
    z_gll = np.fromfile(z_file, dtype='float32').reshape((nspec, 5, 5, 5))
    
    # Apply high velocity anomaly in the middle of x and y, and between -100 to -150 km in z
    for ispec in range(nspec):
        for k in range(5):
            for j in range(5):
                for i in range(5):
                    if -150e3 <= z_gll[ispec, i, j, k] <= -70e3:      
                        if x_gll[ispec, i, j, k] <= 442462.359375+100000  and y_gll[ispec, i, j, k] <=  4369473.75+130000 and  x_gll[ispec, i, j, k] >= 382462.359375+100000  and y_gll[ispec, i, j, k] >= 4349473.75+100000:
                            print('find')
                            vp[ispec, i, j, k] *= 1.1  # Increase velocity by 50%
    vp_modified = np.concatenate(([first_element], vp.flatten(), [last_element]))
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write modified vp to binary file
    vp_modified.tofile(os.path.join(output_dir, f'proc{processor_id}_vp.bin'))

# Example usage for multiple processors:
for proc_id in range(12):
    processor_id_str = f'{proc_id:06d}'
    apply_velocity_anomaly(
        f'DATABASES_MPI/proc{processor_id_str}_vp.bin',
        f'DATABASES_MPI/proc{processor_id_str}_x_gll_recovered.bin',
        f'DATABASES_MPI/proc{processor_id_str}_y_gll_recovered.bin',
        f'DATABASES_MPI/proc{processor_id_str}_z_gll_recovered.bin',
        output_dir='DATABASES_MPI',
        processor_id=processor_id_str
    )

