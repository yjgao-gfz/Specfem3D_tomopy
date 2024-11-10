#!/usr/bin/env bash 

#SBATCH --ntasks=12  
#SBATCH --partition=gpu1
#SBATCH --gres=gpu:1
module load cuda
module swap openmpi mpich/4.1.2
#ml cuda
rm -rf SUCCESS
SPECFEM_HOME=/scratch/gpi/seis/yjgao/Specfem_family/specfem3d-4.1.1_cluster/bin
##hor,ver
mpirun -np 12 $SPECFEM_HOME/xclip_sem -5e-11 5e-11 alpha_kernel_summed $1 $2
mpirun -np 12 $SPECFEM_HOME/xsmooth_sem 2000 1200 alpha_kernel_summed_clip $1 $2
mpirun -np 12 $SPECFEM_HOME/xsmooth_sem 2000 1200 alpha_kernel_summed_clip_smooth $1 $2

#pirun -np 12 $SPECFEM_HOME/xclip_sem -1e-11 1e-11 hess_kernel_summed $1 $2
mpirun -np 12 $SPECFEM_HOME/xsmooth_sem 2000 1200 hess_kernel_summed $1 $2
mpirun -np 12 $SPECFEM_HOME/xsmooth_sem 2000 1200 hess_kernel_summed_smooth $1 $2

rm -rf SUCCESS
touch SUCCESS