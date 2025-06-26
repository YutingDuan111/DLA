import numpy as np
import matplotlib.pyplot as plt
import pickle

class Perimeter:
    def __init__(self):
        self.populate_radius = 50 # don't apply dynamics radius for the first few particles
        self.kill_radius = self.populate_radius
        self.cluster_radius = 0
        self.center = (self.populate_radius, self.populate_radius)

        self.N = self.populate_radius * 2
        self.N_final = self.N
        self.perimeter = np.zeros((self.N, self.N))

        self.lost_particles = 0
        self.attached_particles = 0
        self.launch_count = 0
        self.ETA = 0
        self.perimeter_history = {}  # key: launch_count, value: 'points': points, 'radius': self.perimeter.shape[0]


    def initialize_perimeter(self, core_type="dot", **kwargs):
        mid = self.N // 2
        self.perimeter[mid, mid] = 1

        if core_type == "circle":
            r = kwargs.get("radius", 10)
            for x in range(-r, r + 1):
                for y in range(-r, r + 1):
                    if x**2 + y**2 <= r**2:
                        self.perimeter[mid + y, mid + x] = 1

        elif core_type == "random_walk":
            n = kwargs.get("particles", 50)
            while self.attached_particles < n:
                self.simulate_one_particle()

    
    def expand_perimeter_if_needed(self):
        new_size = int(self.populate_radius*2)  # padding on all sides
        if new_size <= self.N:
            return  # no need to expand

        # create a new big grid, and copy the old grid into the center of new grid
        new_grid = np.zeros((new_size, new_size))
        offset = (new_size - self.N) // 2
        new_grid[offset:offset+self.N, offset:offset+self.N] = self.perimeter

        # update center and radius
        self.center = (self.center[0] + offset, self.center[1] + offset)
        self.perimeter = new_grid
        self.N = new_size
    


    #initial_position is a [y, x]  
    #Takes any input launch point (could be random in the killing radius, or on the perimeter)
    #and walk it until it EITHER reaches the killing radius or attaches to the perimeter. 
    #Returns: # 1) the final position of the particle,
    #         # 2) whether it is lost (True if it reached the killing radius, False if it attached to the perimeter)
    def walk(self, initial_position):
        yi, xi = initial_position
        #fill in the rest
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        while True:
            dy, dx = directions[np.random.randint(8)]
            yi += dy
            xi += dx

            # Check boundaries first to prevent index errors
            if yi <= 1 or yi >= self.N - 2 or xi <= 1 or xi >= self.N - 2:
                return {"final_position": (yi, xi), "lost": True}  # out of bounds, lost
            
            dist = np.sqrt((yi - self.center[0]) ** 2 + (xi - self.center[1]) ** 2)
            if dist > self.kill_radius:
                return {"final_position": (yi, xi), "lost": True}  # out of bounds, lost
            
            if np.any(self.perimeter[yi-1:yi+2, xi-1:xi+2] == 1):
                return {"final_position": (yi, xi), "lost": False} # find the perimeter
    #always return the return structure commmented above. 



    def save_pickle(self, filename="perimeter.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.perimeter_history, f)

    def load_pickle(self, filename="perimeter.pkl"):
        with open(filename, "rb") as f:
            self.perimeter_history = pickle.load(f)
        print(f"Loaded perimeter history from {filename}")
    

    def load_grid(self, filename="perimeter.pkl", timestamp=None):
        with open(filename, "rb") as f:
            self.perimeter_history = pickle.load(f)

        if timestamp is None:
            timestamp = self.launch_count
        else:
            if timestamp not in self.perimeter_history:
                # find the largest key that smaller than timestamp
                available_timestamps = [k for k in self.perimeter_history.keys() if k < timestamp]
                if not available_timestamps:
                    print(f"No data available before timestep {timestamp}.")
                    return
                timestamp = max(available_timestamps)
            
        record = self.perimeter_history[timestamp]
        shape = (record['radius'], record['radius'])
        self.perimeter = np.zeros(shape)
        for y, x in record['points']:
            self.perimeter[y, x] = 1
        self.N = shape[0]
        self.center = (self.N // 2, self.N // 2)
        self.N_final = max(record['radius'] for record in self.perimeter_history.values())
        print(f"Loaded perimeter from timestamp {timestamp}")





    def simulate_one_particle(self, n=1, m=1):
        self.ETA = n/m
        attached = False

    # Step 1: pick random point in populate_radius and let it random walk till attach to the perimeter, record it as a launch point y0, x0
        lost = True
        while lost:
            yi = int(self.center[0] + np.random.randint(-self.populate_radius, self.populate_radius))
            xi = int(self.center[1] + np.random.randint(-self.populate_radius, self.populate_radius))

            result = self.walk((yi, xi))
            (yi, xi), lost = result["final_position"], result["lost"]
            self.launch_count += 1
            if lost:
                self.lost_particles += 1

    # ETA = 1, Step 2: add that point
        if n == 1 and m == 1:
            self.perimeter[yi, xi] = 1
            self.attached_particles += 1
            attached = True

    # ETA > 1, Step 2: launch m particles from that point, and expect all lost
        if n > 1 and m == 1:
            all_escaped = True
            for _ in range(n):
                result = self.walk((yi, xi))
                if not result["lost"]:
                    all_escaped = False
                    break

            if all_escaped:
                self.perimeter[yi, xi] = 1
                self.attached_particles += 1
                attached = True
            else:
                self.lost_particles += 1

    # ETA < 1, Step 2: launch n particles from that point, and expect all returned into the perimeter with diff positions
        if n == 1 and m > 1:
            all_returned = True
            returned_position = [] # use to track if all returned positions are different
            for _ in range(m):
                result = self.walk((yi, xi))
                if result["lost"]:
                    all_returned = False
                    break
                returned_position.append(result["final_position"])
                    
            if all_returned and len(returned_position) == len(set(returned_position)) :
                self.perimeter[yi, xi] = 1
                self.attached_particles += 1
                attached = True
            else:
                self.lost_particles += 1
        

        # update radius + center per 10 times
        if self.attached_particles % 10 == 0:
            # compute update radius
            ys, xs = np.where(self.perimeter == 1)
            self.cluster_radius = np.max(np.sqrt((ys - self.center[0]) ** 2 + (xs - self.center[1]) ** 2))
            self.populate_radius = int(max(self.populate_radius, self.cluster_radius * 3))
            self.kill_radius = self.populate_radius
            self.expand_perimeter_if_needed()
        

        # save the timestamp and current perimeter if sucessfully add a new particle
        if attached:
            ys, xs = np.where(self.perimeter == 1)
            points = list(zip(ys, xs))
            self.perimeter_history[self.launch_count] = {
                'points': points,
                'radius': self.perimeter.shape[0]
            }
            self.N_final = max(self.N_final, self.perimeter.shape[0])


    def get_number_of_particles(self):
        print(f"Launched: {self.launch_count}, Attached: {self.attached_particles}, Lost: {self.lost_particles}")

    def get_grid(self):
        title = f"ETA={self.ETA}"

        canvas = np.zeros((self.N_final, self.N_final))
        # add self.perimeter into the center of canvas
        offset = (self.N_final - self.perimeter.shape[0]) // 2
        y0, x0 = offset, offset
        y1, x1 = y0 + self.perimeter.shape[0], x0 + self.perimeter.shape[1]
        canvas[y0:y1, x0:x1] = self.perimeter
        
        plt.figure(figsize=(6, 6))
        plt.imshow(canvas, cmap='gray')
        plt.title(title)
        plt.axis('off')
        plt.gca().invert_yaxis()
        plt.show()