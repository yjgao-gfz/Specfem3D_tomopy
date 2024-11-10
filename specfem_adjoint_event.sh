#!/usr/bin/env bash 

#SBATCH --ntasks=12  
#SBATCH --partition=gpu1
#SBATCH --gres=gpu:1
module load cuda
module swap openmpi mpich/4.1.2


NPROC=`grep ^NPROC DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`

mkdir -p OUTPUT_FILES/forward_run
rm -rf OUTPUT_FILES/forward_run/*

mv OUTPUT_FILES/timestamp* OUTPUT_FILES/forward_run/
mv OUTPUT_FILES/output_* OUTPUT_FILES/forward_run/
mv OUTPUT_FILES/plot_* OUTPUT_FILES/sr.vtk OUTPUT_FILES/forward_run/
# seismos XX.STA**.
net=XX
mv OUTPUT_FILES/$net.* OUTPUT_FILES/forward_run/

echo "#########################################################"
echo "kernel simulation"
echo "#########################################################"
echo "(running kernel simulation: SIMULATION_TYPE == 3)"
echo
./change_simulation_type.pl -b
# stores output
cp DATA/Par_file DATA/Par_file.kernel
cp DATA/CMTSOLUTION DATA/STATIONS* OUTPUT_FILES/

# runs simulation
if [ "$NPROC" -eq 1 ]; then
  # This is a serial simulation
  echo
  echo "running solver (kernel run)..."
  echo
  ./bin/xspecfem3D
else
  # This is a MPI simulation
  echo
  echo "running solver (kernel run) on $NPROC processors..."
  echo
  mpirun -np $NPROC ./bin/xspecfem3D
fi
# checks exit code
if [[ $? -ne 0 ]]; then exit 1; fi
echo
echo "kernels done"
echo
echo "see results in directory       : OUTPUT_FILES/"
echo "    kernel outputs in directory: $BASEMPIDIR"
echo
echo "done"
echo `date`


touch SUCCESS