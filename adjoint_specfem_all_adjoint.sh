#!/usr/bin/env bash 

echo "Submitting adjoint simulations and capturing job IDs"

for EVENT in EVENT1 EVENT2 EVENT3 EVENT4
do
    cp specfem_adjoint_event.sh $EVENT
    cd $EVENT
    rm -rf SUCCESS
    # Capture the job ID of each submission
    job_id=$(sbatch specfem_adjoint_event.sh | awk '{print $NF}')
    # Print the job ID for Python to capture
    echo "Submitted batch job $job_id for $EVENT"
    cd ..
done