import numpy as np
import os


def sum_alpha_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through each processor
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_alpha_kernel = None

        # Loop through each event directory and sum the kernels
        for event_dir in events_dirs:
            alpha_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_alpha_kernel.bin')
            alpha_kernel = np.fromfile(alpha_kernel_file, dtype='float32')

            if summed_alpha_kernel is None:
                summed_alpha_kernel = alpha_kernel
            else:
                summed_alpha_kernel += alpha_kernel

        # Write the summed alpha kernel to a new file
        summed_alpha_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_alpha_kernel_summed.bin')
        summed_alpha_kernel.tofile(summed_alpha_kernel_file)

        # Copy x, y, z binary files to the output directory
        for coord in ['x', 'y', 'z']:
            coord_file = os.path.join(events_dirs[0], 'DATABASES_MPI', f'proc{processor_id_str}_{coord}.bin')
            output_coord_file = os.path.join(output_dir, f'proc{processor_id_str}_{coord}.bin')
            if os.path.exists(coord_file):
                os.system(f'cp {coord_file} {output_coord_file}')


def sum_beta_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through each processor
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_alpha_kernel = None

        # Loop through each event directory and sum the kernels
        for event_dir in events_dirs:
            alpha_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_beta_kernel.bin')
            alpha_kernel = np.fromfile(alpha_kernel_file, dtype='float32')

            if summed_alpha_kernel is None:
                summed_alpha_kernel = alpha_kernel
            else:
                summed_alpha_kernel += alpha_kernel

        # Write the summed alpha kernel to a new file
        summed_alpha_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_beta_kernel_summed.bin')
        summed_alpha_kernel.tofile(summed_alpha_kernel_file)



def sum_hess_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through each processor
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_alpha_kernel = None

        # Loop through each event directory and sum the kernels
        for event_dir in events_dirs:
            alpha_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_hess_kernel.bin')
            alpha_kernel = np.fromfile(alpha_kernel_file, dtype='float32')

            if summed_alpha_kernel is None:
                summed_alpha_kernel = alpha_kernel
            else:
                summed_alpha_kernel += alpha_kernel

        # Write the summed alpha kernel to a new file
        summed_alpha_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_hess_kernel_summed.bin')
        summed_alpha_kernel.tofile(summed_alpha_kernel_file)

        # Copy x, y, z binary files to the output directory
# Example usage:
events_dirs = ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4']
sum_alpha_kernels(events_dirs,output_dir='SUMMED_KERNELS_l2_ITER5')
sum_beta_kernels(events_dirs,output_dir='SUMMED_KERNELS_l2_ITER5')
sum_hess_kernels(events_dirs,output_dir='SUMMED_KERNELS_l2_ITER5')