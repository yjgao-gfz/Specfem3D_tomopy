import numpy as np
import matplotlib.pyplot as plt
import pyadjoint
import pyadjoint
import obspy
import glob

config=pyadjoint.config.ConfigCrossCorrelation(min_period=2,max_period=40)
obs_waveforms=glob.glob('REF_SEIS/XX*.BXZ.semd')
fh = open('misfit.txt','w')
Misfits_all=0.0
def generate_adj(obsfile,synfile):
    ds1=np.loadtxt(obsfile)
    ds2=np.loadtxt(synfile)
    time_offset=ds1.T[0][0]
    print(time_offset)
    stationname=obsfile.split('/')[-1].split('.')[1]
    channle='BXZ'
    config=pyadjoint.config.ConfigCrossCorrelation(min_period=2,max_period=40)
    obs=obspy.Trace()
    obs.data=ds1.T[1]
    obs.stats.delta=0.02
    obs.stats.network = 'XX'
    obs.stats.station = stationname
    obs.stats.channel = channle
    syn=obspy.Trace()
    syn.data=ds2.T[1]
    syn.stats.delta=0.02
    syn.stats.network = 'XX'
    syn.stats.channel = 'BXZ'
    adjtmp=pyadjoint.adjoint_source.calculate_adjoint_source('cc_traveltime_misfit_new', 
                                obs, syn, config,
                                [[20-time_offset,60-time_offset]],adjoint_src=True, plot=True,plot_filename='OUTPUT_FILES/XX.'+stationname+'_Z.jpg')
    adjtmp.adjoint_source=np.flip(adjtmp.adjoint_source)
    network = 'XX'
    station = stationname
    syn.stats.channel = 'BXZ'
    adjtmp.write(filename='SEM/'+network+'.'+station+'.BXZ'+'.adj',format="SPECFEM", time_offset=time_offset)
    return adjtmp.misfit


for file in obs_waveforms:
    syn='OUTPUT_FILES/'+file.split('/')[1]
    print(syn)
    misfit=generate_adj(file,syn)
    Misfits_all+=misfit


def generate_adj_E(obsfile,synfile):
    ds1=np.loadtxt(obsfile)
    ds2=np.loadtxt(synfile)
    time_offset=ds1.T[0][0]
    stationname=obsfile.split('/')[-1].split('.')[1]
    channle='BXE'
    config=pyadjoint.config.ConfigExponentiatedPhase(min_period=2,max_period=40)
    obs=obspy.Trace()
    obs.data=ds1.T[1]
    obs.stats.delta=0.02
    obs.stats.network = 'XX'
    obs.stats.station = stationname
    obs.stats.channel = channle
    syn=obspy.Trace()
    syn.data=ds2.T[1]
    syn.stats.delta=0.02
    syn.stats.network = 'XX'
    syn.stats.channel = 'BXE'
    adjtmp=pyadjoint.adjoint_source.calculate_adjoint_source('exponentiated_phase_misfit', 
                                obs, syn, config,
                                [[20-time_offset,60-time_offset]],adjoint_src=True, plot=True,plot_filename='OUTPUT_FILES/XX.'+stationname+'_E.jpg')
    adjtmp.adjoint_source=np.flip(adjtmp.adjoint_source)*0
    network = 'XX'
    station = stationname
    syn.stats.channel = 'BXE'
    adjtmp.write(filename='SEM/'+network+'.'+station+'.BXE'+'.adj',format="SPECFEM", time_offset=time_offset)

obs_waveforms=glob.glob('REF_SEIS/XX*.BXE.semd')
for file in obs_waveforms:
    syn='OUTPUT_FILES/'+file.split('/')[1]
    print(syn)
    generate_adj_E(file,syn)


def generate_adj_N(obsfile,synfile):
    ds1=np.loadtxt(obsfile)
    ds2=np.loadtxt(synfile)
    time_offset=ds1.T[0][0]
    stationname=obsfile.split('/')[-1].split('.')[1]
    channle='BXN'
    config=pyadjoint.config.ConfigExponentiatedPhase(min_period=2,max_period=40)
    obs=obspy.Trace()
    obs.data=ds1.T[1]
    obs.stats.delta=0.02
    obs.stats.network = 'XX'
    obs.stats.station = stationname
    obs.stats.channel = channle
    syn=obspy.Trace()
    syn.data=ds2.T[1]
    syn.stats.delta=0.02
    syn.stats.network = 'XX'
    syn.stats.channel = 'BXN'
    adjtmp=pyadjoint.adjoint_source.calculate_adjoint_source('exponentiated_phase_misfit', 
                                obs, syn, config,
                                [[20-time_offset,60-time_offset]],adjoint_src=True, plot=True,plot_filename='OUTPUT_FILES/XX.'+stationname+'_N.jpg')
    adjtmp.adjoint_source=np.flip(adjtmp.adjoint_source)*0
    network = 'XX'
    station = stationname
    syn.stats.channel = 'BXN'
    adjtmp.write(filename='SEM/'+network+'.'+station+'.BXN'+'.adj',format="SPECFEM", time_offset=time_offset)

obs_waveforms=glob.glob('REF_SEIS/XX*.BXN.semd')
for file in obs_waveforms:
    syn='OUTPUT_FILES/'+file.split('/')[1]
    print(syn)
    generate_adj_N(file,syn)

fh.write(str(Misfits_all)+"\n")
