#!/bin/bash
#################################################
it=$1
newdir='REF_SEM_'$it
echo "use the pyadjoint to calculate the adjoint sources"
for EVENT in EVENT1 EVENT2 EVENT3 EVENT4
do 
   echo $EVENT
   rm -rf  $EVENT/adjointsources_l2.py
   rm -rf $EVENT/$newdir
   cp -r adjointsources_l2.py $EVENT
   cd $EVENT
   #cp -r DATABASES_MPI/* $EVENT/DATABASES_MPI/
   python adjointsources_l2.py
   mkdir $newdir
   cp OUTPUT_FILES/*.semd  $newdir
   cp misfit.txt $newdir
   cd ..
done