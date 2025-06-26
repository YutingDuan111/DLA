import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import ETA

plt.style.use('dark_background')

per = ETA.Perimeter()
per.load_grid(timestamp=200)

print(f"Launched: {list(per.perimeter_history.keys())[-1]}")
print(f"Number of particles attached: {len(per.perimeter_history)}")


fig, ax = plt.subplots(figsize=(7, 7), facecolor='black')
ax.set_facecolor('black')
ax.axis('off')

# Selected Colors
colors = ['#000000', '#0a0a1a', '#1a1a33', '#0033ff', '#0066ff', '#00aaff', '#66ccff', '#aaffff', '#ffffff']
n_bins = 256
cmap = LinearSegmentedColormap.from_list('dla_colors', colors, N=n_bins)

frame_keys = sorted(per.perimeter_history.keys())

# Converting each perimeter_history dict to a 2D numpy array for imshow
frames = []
for k in frame_keys:
    record = per.perimeter_history[k]
    radius = record['radius']
    grid = np.zeros((radius, radius), dtype=np.uint8)
    points = record['points']
    if points:
        ys, xs = zip(*points)
        grid[ys, xs] = 1
    frames.append(grid)

def find_structure_bounds(frame):
    ys, xs = np.where(frame == 1)
    if len(xs) == 0:
        return None, None, None, None
    return np.min(xs), np.max(xs), np.min(ys), np.max(ys)

def get_dynamic_extent(frame, padding=50):
    x_min, x_max, y_min, y_max = find_structure_bounds(frame)
    if x_min is None:
        return [0, frame.shape[1], 0, frame.shape[0]]
    
    x_min = max(0, x_min - padding)
    x_max = min(frame.shape[1], x_max + padding)
    y_min = max(0, y_min - padding)
    y_max = min(frame.shape[0], y_max + padding)

    width = x_max - x_min
    height = y_max - y_min
    if width > height:
        diff = width - height
        y_min = max(0, y_min - diff // 2)
        y_max = min(frame.shape[0], y_max + diff // 2)
    elif height > width:
        diff = height - width
        x_min = max(0, x_min - diff // 2)
        x_max = min(frame.shape[1], x_max + diff // 2)
    
    return [x_min, x_max, y_min, y_max]

initial_extent = get_dynamic_extent(frames[0])
im = ax.imshow(frames[0], cmap=cmap, animated=True, extent=initial_extent, interpolation='bilinear')

title = ax.text(0.5, 1.02, "DLA Growth - Launched 0", 
                transform=ax.transAxes, fontsize=16, fontweight='bold',
                ha='center', va='bottom', color='white')

particle_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, 
                        fontsize=12, ha='left', va='top', color='cyan',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

progress_bar = ax.text(0.02, 0.02, "", transform=ax.transAxes,
                       fontsize=10, ha='left', va='bottom', color='lime',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

def animate(frame_idx):
    current_frame = frames[frame_idx]
    current_launch = frame_keys[frame_idx]
    im.set_array(current_frame)

    new_extent = get_dynamic_extent(current_frame)
    im.set_extent(new_extent)

    title.set_text(f"DLA Growth - Launched {current_launch}")

    particle_count = np.sum(current_frame == 1)
    particle_text.set_text(f"Number of Particles Attached: {particle_count}")

    progress = (frame_idx + 1) / len(frames) * 100
    progress_bar.set_text(f"Progress: {progress:.1f}%")

    ax.set_xlim(new_extent[0], new_extent[1])
    ax.set_ylim(new_extent[3], new_extent[2])  # Inverted the Y axis

    return [im, title, particle_text, progress_bar]

anim = animation.FuncAnimation(
    fig, 
    animate, 
    frames=len(frames),
    interval=1,  # 1ms delay between each framesss
    blit=True,
    repeat=True
)

print("Creating DLA gif")
anim.save('DLA.gif', 
          writer='pillow', 
          fps=65,
          dpi=300,
          savefig_kwargs={
              'pad_inches': 0.1,
              'facecolor': 'black'
          })

print("The GIF is saved as 'DLA.gif'")

plt.tight_layout()
plt.show()

def create_final_image():
    print("Creating PNG for the final image")

    fig_final, ax_final = plt.subplots(figsize=(7, 7), facecolor='black')
    ax_final.set_facecolor('black')
    ax_final.axis('off')

    final_frame = frames[-1]
    final_launch = frame_keys[-1]
    final_extent = get_dynamic_extent(final_frame, padding=50)

    ax_final.imshow(final_frame, cmap=cmap, extent=final_extent, interpolation='bilinear')
    ax_final.set_xlim(final_extent[0], final_extent[1])
    ax_final.set_ylim(final_extent[3], final_extent[2])

    ax_final.text(0.5, 1.02, f"DLA Growth - Launched {final_launch}", 
                  transform=ax_final.transAxes, fontsize=16, fontweight='bold',
                  ha='center', va='bottom', color='white')
    final_particles = np.sum(final_frame == 1)
    ax_final.text(0.02, 0.98, f"Number of Particles Attached: {final_particles}", 
                  transform=ax_final.transAxes, fontsize=12, ha='left', va='top', color='cyan',
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
    ax_final.text(0.02, 0.02, "Final Structure - 100.0%", 
                  transform=ax_final.transAxes, fontsize=10, ha='left', va='bottom', color='lime',
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    plt.savefig('DLA_Final.png', dpi=300, bbox_inches='tight', facecolor='black', edgecolor='none')
    plt.show()
    print("Final frame saved as DLA_Final.png")

create_final_image()
