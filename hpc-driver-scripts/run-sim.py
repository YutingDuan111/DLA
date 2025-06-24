import ETA
import sys 
import os
import time 



#output directory should be formatted: /path/to/output/directory/filename.p
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python run-sim.py <n - eta number> <m - eta number> <number of attached particles desired> <output directory with filename>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    attached_particles_desired = int(sys.argv[3])
    if(n < 1 or m < 1 or attached_particles_desired < 1):
        print("n, m, and attached particles desired must be positive integers.")
        sys.exit(1)

    #check that the output directory exists, if not, create it
    filetag = sys.argv[4].split('/')[-1]
    filedir = '/'.join(sys.argv[4].split('/')[:-1]) + '/'
    if(not os.path.exists(filedir)):
        print(f"Output directory {filedir} does not exist. Creating it.")
        os.makedirs(filedir)

    per = ETA.Perimeter()
    per.initialize_perimeter("random_walk", particles=20)



    #I want to incrementally save data in case the HPC cluster cuts our job off
    #before it is complete, because we are unsure of how long these sims will take. 
    save_interval = 1 #hour 
    last_save_time = time.time() # to start, present time


    while(per.attached_particles < attached_particles_desired):
        per.simulate_one_particle(n, m) #sometimes simulates to attach a particle, sometimes doesn't attach a particle. 

        if(per.attached_particles % 100 == 0):
            per.get_number_of_particles() #prints the status


        if(time.time() - last_save_time > save_interval * 3600): #save every hour
            print("Saving data at present status")
            per.get_number_of_particles()
            per.save_grid(sys.argv[4])

    
    print("Simulation complete.")
    per.get_number_of_particles()
    per.save_grid(sys.argv[4])
        




    
