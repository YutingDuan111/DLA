import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from ETA import Perimeter

class DLAAnimator:
    def __init__(self, filename ='perimeter.pkl'):
        self.per = Perimeter()
        self.per.load_pickle(filename)
        self.frame_keys = list(self.per.perimeter_history.keys())
        self.frames = self._build_frames()
        self.colors = ['#000000', '#0a0a1a', '#1a1a33', '#0033ff', '#0066ff', '#00aaff', '#66ccff', '#aaffff', '#ffffff']
        self.n_bins = 256
        self.cmap = LinearSegmentedColormap.from_list('dla_colors', self.colors, N=self.n_bins)
        self.padding = 50

    def _build_frames(self):
        return [
            self._build_grid(record)
            for record in self.per.perimeter_history.values()
        ]

    def _build_grid(self, record):
        grid = np.zeros((record['radius'], record['radius']), dtype=np.uint8)
        if record['points']:
            ys, xs = zip(*record['points'])
            grid[ys, xs] = 1
        return grid

    def find_structure_bounds(self, frame):
        ys, xs = np.where(frame == 1)
        if len(xs) == 0:
            return None, None, None, None
        return np.min(xs), np.max(xs), np.min(ys), np.max(ys)

    def get_dynamic_extent(self, frame):
        x_min, x_max, y_min, y_max = self.find_structure_bounds(frame)
        if x_min is None:
            return [0, frame.shape[1], 0, frame.shape[0]]
        x_min = max(0, x_min - self.padding)
        x_max = min(frame.shape[1], x_max + self.padding)
        y_min = max(0, y_min - self.padding)
        y_max = min(frame.shape[0], y_max + self.padding)
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

    def animate(self, frame_idx):
        current_frame = self.frames[frame_idx]
        current_launch = self.frame_keys[frame_idx]
        self.im.set_array(current_frame)
        new_extent = self.get_dynamic_extent(current_frame)
        self.im.set_extent(new_extent)
        self.title.set_text(f"DLA Growth - Launched {current_launch}")
        particle_count = np.sum(current_frame == 1)
        self.particle_text.set_text(f"Number of Particles Attached: {particle_count}")
        progress = (frame_idx + 1) / len(self.frames) * 100
        self.progress_bar.set_text(f"Progress: {progress:.1f}%")
        self.ax.set_xlim(new_extent[0], new_extent[1])
        self.ax.set_ylim(new_extent[3], new_extent[2])
        return [self.im, self.title, self.particle_text, self.progress_bar]

    def create_animation(self, gif_name='DLA.gif'):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(7, 7), facecolor='black')
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        initial_extent = self.get_dynamic_extent(self.frames[0])
        self.im = self.ax.imshow(self.frames[0], cmap=self.cmap, animated=True, extent=initial_extent, interpolation='bilinear')
        self.title = self.ax.text(0.5, 1.02, "DLA Growth - Launched 0", 
                                  transform=self.ax.transAxes, fontsize=16, fontweight='bold',
                                  ha='center', va='bottom', color='white')
        self.particle_text = self.ax.text(0.02, 0.98, "", transform=self.ax.transAxes, 
                                          fontsize=12, ha='left', va='top', color='cyan',
                                          bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
        self.progress_bar = self.ax.text(0.02, 0.02, "", transform=self.ax.transAxes,
                                         fontsize=10, ha='left', va='bottom', color='lime',
                                         bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
        anim = animation.FuncAnimation(
            self.fig, 
            self.animate, 
            frames=len(self.frames),
            interval=1,
            blit=True,
            repeat=True
        )
        print("Creating DLA gif")
        anim.save(gif_name, 
                  writer='pillow', 
                  fps=65,
                  dpi=300,
                  savefig_kwargs={
                      'pad_inches': 0.1,
                      'facecolor': 'black'
                  })
        print(f"The GIF is saved as '{gif_name}'")
        plt.tight_layout()
        plt.show()

    def create_final_image(self, png_name='DLA_Final.png'):
        print("Creating PNG for the final image")
        fig_final, ax_final = plt.subplots(figsize=(7, 7), facecolor='black')
        ax_final.set_facecolor('black')
        ax_final.axis('off')
        final_frame = self.frames[-1]
        final_launch = self.frame_keys[-1]
        final_extent = self.get_dynamic_extent(final_frame)
        ax_final.imshow(final_frame, cmap=self.cmap, extent=final_extent, interpolation='bilinear')
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
        plt.savefig(png_name, dpi=300, bbox_inches='tight', facecolor='black', edgecolor='none')
        plt.show()
        print(f"Final frame saved as {png_name}")