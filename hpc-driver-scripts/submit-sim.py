import os 


datadir = "/p/lustre2/nexouser/data/StanfordData/angelico/DLA/6-24-2025"

par = [{"job_name": "dla-1-1", "npart": 100000, "n": 1, "m": 1, "duration": "16:00:00"},\
                        {"job_name": "dla-1-2", "npart": 100000, "n": 1, "m": 2, "duration": "1-16:00:00"},\
                        {"job_name": "dla-2-1", "npart": 100000, "n": 2, "m": 1, "duration": "16:00:00"},\
                        {"job_name": "dla-3-2", "npart": 100000, "n": 3, "m": 2, "duration": "1-16:00:00"}]



activate_venv = 'source $HOME/my_personal_env/bin/activate'

jobs_to_submit = [0,1,2,3]

for i in jobs_to_submit:
    filetag = par[i]["job_name"] + ".p"
    datafilepath = datadir+"/"+filetag

    cmd_options = '--export=ALL -p pbatch -t {} -n 1 -J {} -o {} -e {}'.format(par[i]["duration"], par[i]["job_name"], datadir+"/"+par[i]["job_name"]+".out", datadir+"/"+par[i]["job_name"]+".err")
    exe = 'python $HOME/DLA/hpc-driver-scripts/submit-sim.py {:d} {:d} {:d} {}'.format(par[i]["n"], par[i]["m"], par[i]["npart"], datafilepath)
    cmd_full = '{} && sbatch {} --wrap=\'{}\''.format(activate_venv, cmd_options, exe)

    print(cmd_full)
    #os.system(cmd_full)
    print('job submitted {}'.format(par[i]["job_name"]))
    