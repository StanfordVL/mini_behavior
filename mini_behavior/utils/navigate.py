# astar function courtesy of https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
import numpy as np

class AStar_Node():
    """A AStar_node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None, direction=None):
        self.parent = parent
        self.position = position
        self.direction = direction
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end AStar_node
    start_node = AStar_Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = AStar_Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start AStar_node
    open_list.append(start_node)
    
    # Loop until you find the end
    step = 1
    while len(open_list) > 0:
        # print("Step: {}. Open list len: {}".format(step, len(open_list)))
        step += 1
        # Get the current AStar_node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)

        # Found the goal
        if np.all(current_node.position == end_node.position):
            path = []
            current = current_node
            while current is not None:
                # path.append(current.position)
                path.append(current.direction)
                current = current.parent
            return path[::-1][1:] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get AStar_node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[1]][node_position[0]] != 0:
                continue

            # Create new AStar_node
            new_node = AStar_Node(current_node, node_position, new_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
  
            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h
            flag = 0
            # Child is alreadyprint(path, maze) in the open list
            for open_node in open_list:
                if np.all(child.position == open_node.position) and child.f > open_node.f:
                    flag = 1
                    break 

            if flag == 1:
                continue

            # Child is on the closed list
            for closed_child in closed_list:
                if np.all(child.position == closed_child.position) and child.f > closed_child.f:
                    flag = 1 
            
            if flag == 1:
                continue

            # Add the child to the open list
            open_list.append(child)

        closed_list.append(current_node)
    raise ValueError(f"No Path Found from {start} to {end}")


def get_actions(agent_dir, path):
    steps = []
    direction = {(-1, 0): 2, # left
                 (1, 0): 0, # right
                 (0, -1): 3, # up
                 (0, 1): 1 # down
                 }

    # left = 0
    # right = 1
    # forward = 2

    for step in path:
        step_dir = direction[step]
        if (step_dir - agent_dir) % 4 == 1:
            steps.append(1)
        elif (step_dir - agent_dir) % 4 == 2:
            steps += [0, 0]
        elif (step_dir - agent_dir) % 4 == 3:
            steps.append(0)
        agent_dir = step_dir
        steps.append(2)
    return steps


def navigate_between_rooms(start_pos, end_pos, start_room, end_room, maze):
    path = []
    doors = []
    last_pos = start_pos

    room_names = [start_room.name, end_room.name]
    traveling_living_to_bathroom = 'living_room' in room_names and 'bathroom' in room_names
    if end_room in start_room.neighbors and not traveling_living_to_bathroom:
        doors = [start_room.doors[start_room.neighbors.index(end_room)]]
    elif end_room != start_room:   
        if start_room.name == 'bathroom':
            # going to either kitchen or living room
            bedroom = start_room.neighbors[2]
            doors = [start_room.doors[2], bedroom.doors[1]]
            if end_room.name == 'living_room':
                doors.append(end_room.doors[2]) # kitchen to living room
        elif start_room.name == 'bedroom':
            # must be going to living room
            # print("Bedroom doors:", start_room.doors)
            doors = [start_room.doors[1], end_room.doors[2]]
        elif start_room.name == 'kitchen':
            # must be going to bathroom
            doors = [start_room.doors[3], end_room.doors[2]]
        elif start_room.name == 'living_room':
            # going to either bedroom or bathroom
            kitchen = start_room.neighbors[2]
            doors = [start_room.doors[2], kitchen.doors[3]]
            if end_room.name == 'bathroom':
                doors.append(end_room.doors[2])

    if len(doors) > 0:
        # curr pos to first door
        path += astar(maze, last_pos, doors[0].cur_pos)
        last_pos = doors[0].cur_pos
        # Between doors
        for door in doors[1:]:
            path += astar(maze, last_pos, door.cur_pos)
            last_pos = door.cur_pos
        # Last door to goal
        path += astar(maze, last_pos, end_pos)
    else:
        path += astar(maze, last_pos, end_pos)
    return path
