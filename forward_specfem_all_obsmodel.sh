

for EVENT in EVENT1 EVENT2 EVENT3 EVENT4
do
    cp run_forward_event.sh $EVENT
    cd $EVENT
    rm -rf REF_SEIS
    mkdir REF_SEIS
    sbatch run_forward_event.sh
    cd ..
done