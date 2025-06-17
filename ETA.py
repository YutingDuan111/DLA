import numpy as np
import matplotlib.pyplot as plt
import pickle

class Perimeter:
    def __init__(self, N):
        self.N = N
        self.perimeter = np.zeros((N, N))
        self.lost_particles = 0
        self.attached_particles = 0
        self.cluster_radius = 0
        self.populate_radius = 50 # don't apply dynamics radius for the first few particles
        self.kill_radius = self.populate_radius
        self.center = (N // 2, N // 2)
        self.launch_count = 0
        self.perimeter_history = {}  # key: launch_count, value: perimeter
        self.ETA = None


    def initialize_perimeter(self, core_type="dot", **kwargs):
        mid = self.N // 2

        if core_type == "dot":
                self.perimeter[mid, mid] = 1

        elif core_type == "circle":
            r = kwargs.get("radius", 10)
            for x in range(-r, r + 1):
                for y in range(-r, r + 1):
                    if x**2 + y**2 <= r**2:
                        self.perimeter[mid + y, mid + x] = 1

        elif core_type == "random_walk":
            n = kwargs.get("particles", 50)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
            self.perimeter[mid, mid] = 1

            for _ in range(n):
                    x = np.random.randint(1, self.N - 1)
                    y = np.random.randint(1, self.N - 1)

                    while True:                
                        # take steps
                        dy, dx = directions[np.random.randint(8)]
                        x += dx
                        y += dy

                        # check if the particle move out of the range
                        if x <= 1 or x >= self.N - 2 or y <= 1 or y >= self.N - 2:
                            break  # particle is lost
                        if np.any(self.perimeter[y-1:y+2, x-1:x+2] == 1):
                            self.perimeter[y, x] = 1
                            break

        else:
            raise ValueError("Unknown core_type")


    def compute_mass_center(self):
        ys, xs = np.where(self.perimeter == 1)
        cy = int(np.mean(ys))
        cx = int(np.mean(xs))
        return cy, cx
    
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
    

    def save_grid(self, filename="perimeter.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.perimeter_history, f)
    
    def load_grid(self, filename="perimeter.pkl", timestep=None):
        with open(filename, "rb") as f:
            self.perimeter_history = pickle.load(f)
        if timestep is not None:
            record = self.perimeter_history[timestep]
            shape = (record['radius'], record['radius'])
            self.perimeter = np.zeros(shape)
            for y, x in record['points']:
                self.perimeter[y, x] = 1
            self.N = shape[0]
            self.center = (self.N // 2, self.N // 2)


    #initial_position is a [y, x]  
    #Takes any input launch point (could be random in the killing radius, or on the perimeter)
    #and walk it until it EITHER reaches the killing radius or attaches to the perimeter. 
    #Returns: # 1) the final position of the particle,
    #         # 2) whether it is lost (True if it reached the killing radius, False if it attached to the perimeter)
    def walk(self, initial_position):
        yi, xi = initial_position
        #fill in the rest

        #always return the return structure commmented above. 

        return {"final_position": (yi, xi), "lost": False} #example

        

    def simulate_one_particle(self, n=1, m=1):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        self.ETA = n/m

        # Step 1: pick random point in populate_radius and let it random walk till attach to the perimeter, record it as a lauch point y0, x0
        while True:
            x = int(self.center[0] + np.random.randint(-self.populate_radius, self.populate_radius))
            y = int(self.center[1] + np.random.randint(-self.populate_radius, self.populate_radius))

            # if x <= 1 or x >= self.N - 2 or y <= 1 or y >= self.N - 2:
            #     continue  # out of bounds, restart
            
            found_launch_point = False
            while True:
                dy, dx = directions[np.random.randint(8)]
                y += dy
                x += dx

                dist = np.sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2)
                if dist > self.kill_radius or x <= 1 or x >= self.N - 2 or y <= 1 or y >= self.N - 2:
                    if self.ETA == 1:
                        self.lost_particles += 1
                    break  # out of bounds again, restart loop
                if np.any(self.perimeter[y-1:y+2, x-1:x+2] == 1):
                    y0, x0 = y, x  # record valid launch point
                    found_launch_point = True
                    if self.ETA == 1:
                        self.attached_particles += 1
                        self.perimeter[y, x] = 1
                    break

            if not found_launch_point:
                continue  # did not find a valid launch point, try again
            else:
                break  # got valid launch point

        if(self.ETA>1):
            #ETA>1, Step 2: launch eta particles from that point, and expect all lost
            all_escaped = True
            for _ in range(n):
                y, x = y0, x0

                while all_escaped:
                    dy, dx = directions[np.random.randint(8)]
                    y += dy
                    x += dx
                    
                    # check if the individual walker is lost
                    dist = np.sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2)
                    if dist > self.kill_radius or x <= 1 or x >= self.N - 2 or y <= 1 or y >= self.N - 2:
                        break  
                    if np.any(self.perimeter[y-1:y+2, x-1:x+2] == 1):
                        all_escaped = False
                        break  # one walker attached

            if all_escaped:
                self.perimeter[y0, x0] = 1
                self.attached_particles += 1
            else:
                self.lost_particles += 1

        if(self.ETA<1):
            # ETA<1, Step 2: launch eta particles from that point, and expect all returned into the perimeter
            all_returned = True
            returned_position = []
            for _ in range(m):
                y, x = y0, x0

                while all_returned:
                    dy, dx = directions[np.random.randint(8)]
                    y += dy
                    x += dx
                    
                    # check if the individual walker is returned
                    dist = np.sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2)
                    if dist > self.kill_radius or x <= 1 or x >= self.N - 2 or y <= 1 or y >= self.N - 2:
                        all_returned = False
                        break  
                    if np.any(self.perimeter[y-1:y+2, x-1:x+2] == 1):
                        returned_position.append((y, x))
                        break  # one walker attached

            if (all_returned and len(returned_position) == len(set(returned_position)) ):
                self.perimeter[y0, x0] = 1
                self.attached_particles += 1
            else:
                self.lost_particles += 1
        

        # update radius + center per 10 times
        if self.attached_particles % 10 == 0:
            # update center dynamically
            # self.center = self.compute_mass_center()
            # compute update radius
            ys, xs = np.where(self.perimeter == 1)
            self.cluster_radius = np.max(np.sqrt((ys - self.center[0]) ** 2 + (xs - self.center[1]) ** 2))
            self.populate_radius = int(max(self.populate_radius, self.cluster_radius * 3))
            self.kill_radius = self.populate_radius
            self.expand_perimeter_if_needed()
        
        # save the timestamp and current perimeter
        self.launch_count += 1
        ys, xs = np.where(self.perimeter == 1)
        points = list(zip(ys, xs))
        self.perimeter_history[self.launch_count] = {
            'points': points,
            'radius': self.perimeter.shape[0]
        }
        # self.perimeter_history[self.launch_count] = self.perimeter.copy()

    def get_number_of_particles(self):
        print(f"Attached: {self.attached_particles}, Lost: {self.lost_particles}")

    def get_grid(self):
        title = f"ETA={self.ETA}"
        plt.figure(figsize=(6, 6))
        plt.imshow(self.perimeter, cmap='gray')
        plt.title(title)
        plt.axis('off')
        plt.gca().invert_yaxis()
        plt.show()