# FROM MINIGRID REPO
import sys
import numpy as np

# Only ask users to install matplotlib if they actually need it
try:
    import matplotlib.pyplot as plt
except:
    print('To display the environment in a window, please install matplotlib, eg:')
    print('pip3 install --user matplotlib')
    sys.exit(-1)

class Window:
    """
    Window to draw a gridworld instance using Matplotlib
    """

    def __init__(self, title):
        self.fig = None

        self.imshow_obj = None

        # Create the figure and axes
        self.fig, (self.ax_on, self.ax_carry, self.ax) = plt.subplots(ncols=3, figsize=(5, 10), gridspec_kw={'width_ratios': [1, 1, 3]})

        # Show the env name in the window title
        self.fig.canvas.set_window_title(title)

        # Turn off x/y axis numbering/ticks
        self.ax.xaxis.set_ticks_position('none')
        self.ax.yaxis.set_ticks_position('none')
        _ = self.ax.set_xticklabels([])
        _ = self.ax.set_yticklabels([])

        # Flag indicating the window was closed
        self.closed = False

        def close_handler(evt):
            self.closed = True

        self.fig.canvas.mpl_connect('close_event', close_handler)

    def show_img(self, img):
        """
        Show an image or update the image being shown
        """

        # If no image has been shown yet,
        # show the first image of the environment
        if self.imshow_obj is None:
            self.imshow_obj = self.ax.imshow(img, interpolation='bilinear')

        # Update the image data
        self.imshow_obj.set_data(img)

        # Request the window be redrawn
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

        # Let matplotlib process UI events
        plt.pause(0.001)

    def set_caption(self, text):
        """
        Set/update the caption text below the image
        """

        plt.xlabel(text)

    # NEW
    def set_inventory(self, env):
        """
        Set/update the inventory of objects
        """
        def create_text(list):
            text = ""
            for elem in list:
                text += "{}\n".format(elem)
            return text

        def create_inv(ax, title, text):
            ax.clear()
            ax.axis('off')
            self.ax_on.set_ylim(0, 1)

            ax.text(0.5, 0.25, title, rotation=0, ha='center', va='center')
            ax.text(0.5, 0.5, text, rotation=0, ha='center', va='center')

        on_grid = []
        carrying = [obj.name for obj in env.carrying]
        for objs in env.objs.values():
            for obj in objs:
                if obj.name not in carrying:
                    on_grid.append(obj.name)

        text_1 = create_text(on_grid)
        text_2 = create_text(carrying)

        create_inv(self.ax_on, "ON_GRID", text_1)
        create_inv(self.ax_carry, "CARRYING", text_2)

        plt.tight_layout()

    def reg_key_handler(self, key_handler):
        """
        Register a keyboard event handler
        """

        # Keyboard handler
        self.fig.canvas.mpl_connect('key_press_event', key_handler)

    def show(self, block=True):
        """
        Show the window, and start an event loop
        """

        # If not blocking, trigger interactive mode
        if not block:
            plt.ion()

        # Show the plot
        # In non-interative mode, this enters the matplotlib event loop
        # In interactive mode, this call does not block
        plt.show()

    def close(self):
        """
        Close the window
        """

        plt.close()
        self.closed = True
