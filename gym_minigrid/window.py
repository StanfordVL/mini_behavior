# FROM MINIGRID REPO
import sys
import numpy as np

# Only ask users to install matplotlib if they actually need it
try:
    # import matplotlib
    # matplotlib.use('TKAgg')
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
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
        self.closeup_obj = {'base': None,
                            'top': None,
                            'middle': None,
                            'bottom': None
                            }

        # Create the figure and axes
        self.fig = plt.figure()

        window = gridspec.GridSpec(1, 6, figure=self.fig)

        self.inventory = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=window[0])
        self.grid = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=window[1:5])
        self.closeup = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=window[5])

        self.on_grid_ax = self.fig.add_subplot(self.inventory[:1, :])
        self.carrying_ax = self.fig.add_subplot(self.inventory[1:, :])
        self.grid_ax = self.fig.add_subplot(self.grid[:, :], aspect='equal')
        self.grid_ax.set_aspect('equal')
        self.grid_ax.set_anchor('N')

        self.on_grid_ax.set_title('on grid', fontsize=8, pad=3)
        self.carrying_ax.set_title('carrying', fontsize=8, pad=3)

        base_ax = self.fig.add_subplot(self.closeup[:1, :])
        ontop_ax = self.fig.add_subplot(self.closeup[1:2, :])
        inside_ax = self.fig.add_subplot(self.closeup[2:3, :])
        under_ax = self.fig.add_subplot(self.closeup[3:4, :])

        self.closeup_axes = {'base': base_ax,
                             'top': ontop_ax,
                             'middle': inside_ax,
                             'bottom': under_ax
                             }

        for name, ax in self.closeup_axes.items():
            ax.set_aspect('equal')
            ax.set_title(name, fontsize=8, pad=3)
            ax.set_anchor('N')

            self.closeup_obj[name] = ax.imshow(np.zeros(shape=(1,1,3)), interpolation='bilinear')


        # Show the env name in the window title
        self.fig.canvas.set_window_title(title)

        # Turn off x/y axis numbering/ticks
        for i, ax in enumerate(self.fig.axes):
            ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

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
            self.imshow_obj = self.grid_ax.imshow(img, interpolation='bilinear')

        # Update the image data
        self.imshow_obj.set_data(img)

        # Request the window be redrawn
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

        # Let matplotlib process UI events
        plt.pause(0.0001)

    def set_caption(self, text):
        """
        Set/update the caption text below the image
        """
        # plt.xlabel(text)
        self.grid_ax.set_xlabel(text, labelpad=10)

    # NEW
    def set_inventory(self, env):
        """
        Set/update the inventory of objects
        """
        def gen_inv(ax, objs):
            # gen text
            text = ""
            for elem in objs:
                text += "{}\n".format(elem)

            # add to plot
            ax.clear()
            # ax.set_ylim(0, 1)
            ax.text(0.5, 0.5, text, rotation=0, ha='center', va='center')

        on_grid = []
        carrying = [obj.name for obj in env.obj_instances.values() if obj.check_abs_state(env, 'inhandofrobot')]
        for objs in env.objs.values():
            for obj in objs:
                if obj.name not in carrying and obj.type != 'door':
                    on_grid.append(obj.name)

        gen_inv(self.on_grid_ax, on_grid)
        gen_inv(self.carrying_ax, carrying)

        self.on_grid_ax.set_title('on grid', fontsize=8, pad=3)
        self.carrying_ax.set_title('carrying', fontsize=8, pad=3)

    def show_closeup(self, imgs):
        for name, ax in self.closeup_axes.items():
            NAME_INT_MAP = {'base': 0, 'top': 1, 'middle': 2, 'bottom': 3}
            img = imgs[NAME_INT_MAP[name]]

            # Update the image data
            self.closeup_obj[name].set_data(img)

            # Request the window be redrawn
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def no_closeup(self):
        for ax in self.closeup_obj.values():
            if ax is not None:
                ax.set_data(np.zeros(shape=(1,1,3)))

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
        # In non-interactive mode, this enters the matplotlib event loop
        # In interactive mode, this call does not block
        plt.show()

    def close(self):
        """
        Close the window
        """

        plt.close()
        self.closed = True
