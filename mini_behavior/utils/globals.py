import numpy as np

# Map of color names to RGB values
COLORS = {
    'red'   : np.array([128, 0, 32]),
    'green' : np.array([0, 255, 0]),
    'blue'  : np.array([0, 0, 255]),
    'purple': np.array([112, 39, 195]),
    'yellow': np.array([255, 255, 0]),
    'grey'  : np.array([100, 100, 100]),
    'orange': np.array([255, 165, 0]),
    'white' : np.array([255, 255, 255]),
    'l_green': np.array([46, 139, 87]),
    'brown': np.array([101, 67, 33]),
    'pink': np.array([255, 192, 203]),
    'l_blue': np.array([48, 132, 158]),
    'tan': np.array([176, 142, 103]),
    'black': np.array([0, 0, 0])
}

COLOR_NAMES = sorted(list(COLORS.keys()))

# Used to map colors to integers
COLOR_TO_IDX = {
    'red': 0,
    'green': 1,
    'blue': 2,
    'purple': 3,
    'yellow': 4,
    'grey': 5,
    'orange': 6,
    'white': 7,
    'l_green': 8,
    'brown': 9,
    'pink': 10,
    'l_blue': 11,
    'tan': 12,
    'black': 13
}

IDX_TO_COLOR = dict(zip(COLOR_TO_IDX.values(), COLOR_TO_IDX.keys()))

# Map of agent direction indices to vectors
DIR_TO_VEC = [
    # Pointing right (positive X)
    np.array((1, 0)),
    # Down (positive Y)
    np.array((0, 1)),
    # Pointing left (negative X)
    np.array((-1, 0)),
    # Up (negative Y)
    np.array((0, -1)),
]
