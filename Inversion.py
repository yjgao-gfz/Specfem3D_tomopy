import os
import glob
import subprocess
import numpy as np
import shutil
import time

def run_simulation(script_path='forward_specfem_all_synmodel.sh'):
    """
    Run the bash script to start the simulations and capture job IDs.
    """
    print("Starting the simulations with the bash script...")
    result = subprocess.run(['bash', script_path], capture_output=True, text=True)
    if result.returncode == 0:
        print("Simulations initiated successfully.")
        job_ids = [line.split()[-1] for line in result.stdout.splitlines() if "Submitted batch job" in line]
        print("Submitted Job IDs:", job_ids)
        return job_ids
    else:
        print("Error initiating simulations:")
        print(result.stderr)
        return []

def check_job_status(job_ids):
    """
    Check the status of jobs by their job IDs using squeue.
    """
    job_status = {}
    result = subprocess.run(['squeue', '--jobs', ','.join(job_ids), '--format=%A %T', '--noheader'], 
                            capture_output=True, text=True)
    for line in result.stdout.splitlines():
        job_id, status = line.split()
        job_status[job_id] = status
    return job_status

def check_simulation_status(event_dirs, job_ids, success_file='SUCCESS', check_interval=10):
    """
    Monitor the status of multiple simulations until all are complete or failed.
    """
    while True:
        all_completed = True
        job_status = check_job_status(job_ids)
        
        # Print job status and check for completion
        for job_id, status in job_status.items():
            print(f"Job {job_id} Status: {status}")
            if status in ['PENDING', 'RUNNING']:
                all_completed = False

        # Check for SUCCESS files in each event directory
        for event in event_dirs:
            event_status_file = os.path.join(event, success_file)
            if os.path.exists(event_status_file):
                print(f"{event}: SUCCESS")
            else:
                print(f"{event}: INCOMPLETE OR FAILED")
                all_completed = False

        if all_completed:
            print("All simulations completed successfully!")
            break

        print(f"Checking again in {check_interval} seconds...\n")
        time.sleep(check_interval)

def run_create_adjoint_sources(iteration):
    """
    Run the create_adjoint_sources.sh script with the current iteration number.
    """
    print(f"Running create_adjoint_sources.sh for iteration {iteration}...")
    result = subprocess.run(['bash', 'create_adjoint_sources.sh', str(iteration)], capture_output=True, text=True)
    if result.returncode == 0:
        print("Adjoint sources created successfully.")
    else:
        print("Error running create_adjoint_sources.sh:")
        print(result.stderr)

def calculate_misfit(iteration):
    """
    Calculate the total misfit for the given iteration by summing misfits from all events.
    """
    total_misfit = 0
    for event in glob.glob('EVENT*'):
        misfit_file = os.path.join(event, f'REF_SEM_{iteration}', 'misfit.txt')
        if os.path.exists(misfit_file):
            misfit = np.loadtxt(misfit_file)
            total_misfit += misfit
            print(f"Misfit for {event}: {misfit}")
        else:
            print(f"Warning: Misfit file not found for {event}")
    print(f"Total misfit for iteration {iteration}: {total_misfit}")
    return total_misfit

def compare_misfits(prev_misfit, current_misfit, threshold=0.005):
    """
    Compare the misfit from the previous iteration with the current iteration.
    If the misfit drops by more than 0.5%, continue with adjoint simulations.
    """
    difference = current_misfit - prev_misfit
    percent_change = (difference / prev_misfit) * 100
    print(f"Previous Misfit: {prev_misfit}, Current Misfit: {current_misfit}")
    print(f"Misfit Change: {difference} ({percent_change:.2f}%)")
    
    if percent_change < -threshold * 100:
        print("Misfit dropped by over 0.5%; proceeding to submit adjoint simulations.")
        stop=False
    else:
        print("Misfit did not drop significantly; stopping inversion process.")
        stop=True
    return stop


def run_adjoint_simulations():
    """
    Run the adjoint_specfem_all_adjoint.sh script to submit adjoint simulations and capture job IDs.
    """
    print("Submitting adjoint simulations...")
    result = subprocess.run(['bash', 'adjoint_specfem_all_adjoint.sh'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Adjoint simulations submitted successfully.")
        adjoint_job_ids = [line.split()[-1] for line in result.stdout.splitlines() if "Submitted batch job" in line]
        print("Submitted Adjoint Job IDs:", adjoint_job_ids)
        return adjoint_job_ids
    else:
        print("Error submitting adjoint simulations:")
        print(result.stderr)
        return []

def sum_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    """
    Sum alpha, beta, and hess kernels across events for each processor.
    """
    print("Summing alpha, beta, and hess kernels.")
    sum_alpha_kernels(events_dirs, output_dir, processor_count)
    sum_beta_kernels(events_dirs, output_dir, processor_count)
    sum_hess_kernels(events_dirs, output_dir, processor_count)

def sum_alpha_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    os.makedirs(output_dir, exist_ok=True)
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_alpha_kernel = None
        for event_dir in events_dirs:
            alpha_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_alpha_kernel.bin')
            alpha_kernel = np.fromfile(alpha_kernel_file, dtype='float32')
            if summed_alpha_kernel is None:
                summed_alpha_kernel = alpha_kernel
            else:
                summed_alpha_kernel += alpha_kernel
        summed_alpha_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_alpha_kernel_summed.bin')
        summed_alpha_kernel.tofile(summed_alpha_kernel_file)

def sum_beta_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    os.makedirs(output_dir, exist_ok=True)
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_beta_kernel = None
        for event_dir in events_dirs:
            beta_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_beta_kernel.bin')
            beta_kernel = np.fromfile(beta_kernel_file, dtype='float32')
            if summed_beta_kernel is None:
                summed_beta_kernel = beta_kernel
            else:
                summed_beta_kernel += beta_kernel
        summed_beta_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_beta_kernel_summed.bin')
        summed_beta_kernel.tofile(summed_beta_kernel_file)

def sum_hess_kernels(events_dirs, output_dir='SUMMED_KERNELS', processor_count=12):
    os.makedirs(output_dir, exist_ok=True)
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        summed_hess_kernel = None
        for event_dir in events_dirs:
            hess_kernel_file = os.path.join(event_dir, 'DATABASES_MPI', f'proc{processor_id_str}_hess_kernel.bin')
            hess_kernel = np.fromfile(hess_kernel_file, dtype='float32')
            if summed_hess_kernel is None:
                summed_hess_kernel = hess_kernel
            else:
                summed_hess_kernel += hess_kernel
        summed_hess_kernel_file = os.path.join(output_dir, f'proc{processor_id_str}_hess_kernel_summed.bin')
        summed_hess_kernel.tofile(summed_hess_kernel_file)

def run_smooth_kernel(input_dir='SUMMED_KERNELS', output_dir='SUMMED_KERNELS'):
    """
    Run smooth_kernel.sh to smooth the summed kernels and monitor its status.
    """
    print("Submitting smoothing job for kernels.")
    result = subprocess.run(['sbatch', 'smooth_kernel.sh', input_dir, output_dir], capture_output=True, text=True)
    
    if result.returncode == 0:
        job_id = result.stdout.strip().split()[-1]
        print(f"Smoothing job submitted with Job ID: {job_id}")
        monitor_smoothing_job(job_id)
    else:
        print("Error submitting smoothing job:")
        print(result.stderr)

def monitor_smoothing_job(job_id, check_interval=10):
    """
    Monitor the smoothing job by checking the job ID status until completion.
    """
    print(f"Monitoring smoothing job {job_id}...")
    while True:
        job_status = check_job_status([job_id])
        status = job_status.get(job_id, "COMPLETED")

        if status == "COMPLETED":
            print(f"Smoothing job {job_id} completed successfully!")
            break
        elif status in ["PENDING", "RUNNING"]:
            print(f"Smoothing job {job_id} Status: {status}")
        else:
            print(f"Smoothing job {job_id} encountered an issue: {status}")
            break

        time.sleep(check_interval)

def gauss_newton_update(model_dir='MODEL_1', kernel_dir='SUMMED_KERNELS',
                        output_dir='MODEL_2_test', perturb_vp=0.01, perturb_vs=0.01, processor_count=12, update_vs=True):
    """
    Update the velocity model using Gauss-Newton method with known diagonal Hessian.
    """
    os.makedirs(output_dir, exist_ok=True)
    databases_mpi_dir = 'DATABASES_MPI'
    hess_dir = kernel_dir
    
    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        vp_file = os.path.join(model_dir, f'proc{processor_id_str}_vp.bin')
        vp = np.fromfile(vp_file, dtype='float32')
        vp_first, vp_last = vp[0], vp[-1]
        vp = vp[1:-1]

        vs_file = os.path.join(model_dir, f'proc{processor_id_str}_vs.bin') if update_vs else None
        if update_vs:
            vs = np.fromfile(vs_file, dtype='float32')
            vs_first, vs_last = vs[0], vs[-1]
            vs = vs[1:-1]

        # Load kernels for gradients
        vp_kernel_file = os.path.join(kernel_dir, f'proc{processor_id_str}_alpha_kernel_summed_clip_smooth_smooth.bin')
        vp_kernel = np.fromfile(vp_kernel_file, dtype='float32')[1:-1]

        if update_vs:
            vs_kernel_file = os.path.join(kernel_dir, f'proc{processor_id_str}_beta_kernel_summed_clip_smooth_smooth.bin')
            vs_kernel = np.fromfile(vs_kernel_file, dtype='float32')[1:-1]

        # Load diagonal Hessian elements for VP and VS
        vp_hess_file = os.path.join(hess_dir, f'proc{processor_id_str}_hess_kernel_summed_smooth_smooth.bin')
        vp_hessian = np.fromfile(vp_hess_file, dtype='float32')[1:-1]

        update_vp = vp - perturb_vp * vp_kernel / (vp_hessian + 5e-14)
        update_vp = np.concatenate(([vp_first], update_vp, [vp_last]))

        if update_vs:
            vs_hess_file = os.path.join(hess_dir, f'proc{processor_id_str}_hess_kernel_summed_smooth_smooth.bin')
            vs_hessian = np.fromfile(vs_hess_file, dtype='float32')[1:-1]
            update_vs = vs - (perturb_vs * vs_kernel / vs_hessian)
            update_vs = np.concatenate(([vs_first], update_vs, [vs_last]))

        # Write the updated model files
        update_vp.tofile(os.path.join(output_dir, f'proc{processor_id_str}_vp.bin'))
        if update_vs:
            update_vs.tofile(os.path.join(output_dir, f'proc{processor_id_str}_vs.bin'))

        shutil.copy(os.path.join(output_dir, f'proc{processor_id_str}_vp.bin'), os.path.join(databases_mpi_dir, f'proc{processor_id_str}_vp.bin'))
        if update_vs:
            shutil.copy(os.path.join(output_dir, f'proc{processor_id_str}_vs.bin'), os.path.join(databases_mpi_dir, f'proc{processor_id_str}_vs.bin'))

    for proc_id in range(processor_count):
        processor_id_str = f'{proc_id:06d}'
        for coord in ['x', 'y', 'z']:
            coord_file = os.path.join(model_dir, f'proc{processor_id_str}_{coord}.bin')
            # shutil.copy(coord_file, os.path.join(databases_mpi_dir, f'proc{processor_id_str}_{coord}.bin'))
import os
import datetime

def log_iteration(iteration, prev_misfit, current_misfit, stop):
    """
    Logs the details of each iteration into a separate report file.

    Args:
        iteration (int): Current iteration number.
        prev_misfit (float): Misfit value from the previous iteration.
        current_misfit (float): Misfit value for the current iteration.
        stop (bool): Whether the inversion process should stop (convergence).
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"inversion_report_iteration_{iteration}.txt")

    percent_change = (current_misfit - prev_misfit) / prev_misfit * 100 if prev_misfit != 0 else 0
    status = "Converged" if stop else "Continuing to Next Iteration"

    with open(log_file, "w") as f:
        f.write(f"Iteration: {iteration}\n")
        f.write(f"Timestamp: {datetime.datetime.now()}\n")
        f.write(f"Previous Misfit: {prev_misfit}\n")
        f.write(f"Current Misfit: {current_misfit}\n")
        f.write(f"Misfit Change: {percent_change:.2f}%\n")
        f.write(f"Status: {status}\n")
        f.write("-" * 40 + "\n")

    print(f"Log for iteration {iteration} saved to {log_file}")

# Define workflow parameters
def inversion_iteration(current_iteration,event_dirs):
    print('new model is created and will launch simulations for iteration', current_iteration)
    gauss_newton_update(
        model_dir=f'MODEL_{current_iteration-1}_test/',
        kernel_dir=f'SUMMED_KERNELS_l2_ITER{current_iteration-1}/',
        output_dir=f'MODEL_{current_iteration}_test',
        perturb_vp=1,
        perturb_vs=1,
        processor_count=12,
        update_vs=False
        )
    job_ids = run_simulation()
    if job_ids:
        check_simulation_status(event_dirs, job_ids)

    # Run the adjoint source creation after simulations are complete
        run_create_adjoint_sources(current_iteration)

    # Calculate misfit for the current and previous iterations
        current_misfit = calculate_misfit(current_iteration)
        previous_misfit = calculate_misfit(current_iteration - 1)  # Assuming previous iteration exists

    # Compare misfits and decide on adjoint simulation submission
    else:
        print("No jobs were submitted.")

    print('forward simulations are finished')

    stop=compare_misfits(previous_misfit, current_misfit)

    if stop==False:
        print('start adjoint simulations')
        adjoint_job_ids = run_adjoint_simulations()
        if job_ids:
            check_simulation_status(event_dirs, adjoint_job_ids)
        else:
            print("No jobs were submitted.")



    # Sum the kernels after adjoint simulations complete
        sum_kernels(event_dirs, output_dir=f'SUMMED_KERNELS_l2_ITER{current_iteration}')

    # Run smoothing on the summed kernels
        run_smooth_kernel(input_dir=f'SUMMED_KERNELS_l2_ITER{current_iteration}', output_dir=f'SUMMED_KERNELS_l2_ITER{current_iteration}')
    else:
        print('converged')


    log_iteration(current_iteration, previous_misfit, current_misfit, stop)
