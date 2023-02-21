from gym_minigrid.window import *
import matplotlib.gridspec as gridspec


class Window(Window):
    """
    Window to draw a gridworld instance using Matplotlib
    """

    def __init__(self, title):
        self.no_image_shown = True
        self.imshow_obj = None
        self.closeup_obj = {'top': None,
                            'middle': None,
                            'bottom': None,
                            'container': None,
                            }

        # Create the figure and axes
        self.fig = plt.figure()

        window = gridspec.GridSpec(1, 6, figure=self.fig)

        self.inventory = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=window[0])
        self.grid = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=window[1:5])
        self.closeup = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=window[5])

        self.on_grid_ax = self.fig.add_subplot(self.inventory[:1, :])
        self.carrying_ax = self.fig.add_subplot(self.inventory[1:, :])
        self.ax = self.fig.add_subplot(self.grid[:, :], aspect='equal')
        self.ax.set_aspect('equal')
        self.ax.set_anchor('N')

        self.on_grid_ax.set_title('on grid', fontsize=8, pad=3)
        self.carrying_ax.set_title('carrying', fontsize=8, pad=3)

        top_ax = self.fig.add_subplot(self.closeup[:1, :])
        middle_ax = self.fig.add_subplot(self.closeup[1:2, :])
        bottom_ax = self.fig.add_subplot(self.closeup[2:3, :])
        container_ax = self.fig.add_subplot(self.closeup[3:4, :])

        self.closeup_axes = {'top': top_ax,
                             'middle': middle_ax,
                             'bottom': bottom_ax,
                             'container': container_ax,
                             }

        for name, ax in self.closeup_axes.items():
            ax.set_aspect('equal')
            ax.set_title(name, fontsize=8, pad=3)
            ax.set_anchor('N')

            self.closeup_obj[name] = ax.imshow(np.zeros(shape=(1,1,3)), interpolation='bilinear')

        # Show the env name in the window title
        self.fig.canvas.manager.set_window_title(title)

        # Turn off x/y axis numbering/ticks
        for i, ax in enumerate(self.fig.axes):
            ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

        # Flag indicating the window was closed
        self.closed = False

        def close_handler(evt):
            self.closed = True

        self.fig.canvas.mpl_connect('close_event', close_handler)

    def set_caption(self, text):
        """
        Set/update the caption text below the image
        """
        self.ax.set_xlabel(text, labelpad=10)

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
            NAME_INT_MAP = {'container': 0, 'bottom': 1, 'middle': 2, 'top': 3}
            img = imgs[NAME_INT_MAP[name]]
            # Update the image data
            self.closeup_obj[name].set_data(img)
            self.closeup_axes[name].set_title(name, fontsize=8, pad=3)

            # Request the window be redrawn
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def no_closeup(self):
        for name, ax in self.closeup_axes.items():
            ax.set_title('')
            if self.closeup_obj[name] is not None:
                self.closeup_obj[name].set_data(np.ones(shape=(1,1,3)))

    def save_img(self, out_filepath):
        self.fig.savefig(out_filepath)
