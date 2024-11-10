echo "Copying the Par_file and DATABASES to event directory"
for EVENT in EVENT1 EVENT2 EVENT3 EVENT4
do
   cp -r DATA/Par_file $EVENT/DATA/Par_file
   cp -r DATABASES_MPI/* $EVENT/DATABASES_MPI/
done

echo "Running the forward simulation with new model"

for EVENT in EVENT1 EVENT2 EVENT3 EVENT4
do
    cp Specfem_FWI_for_event.sh $EVENT
    cd $EVENT
    rm -rf SUCCESS
    # Capture the job ID of each sbatch submission
    job_id=$(sbatch Specfem_FWI_for_event.sh | awk '{print $NF}')
    echo "Submitted batch job $job_id"  # Only output the job ID line for Python to parse
    cd ..
done
