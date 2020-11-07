from p1_support import load_level, show_level, save_level_costs
import math
from heapq import heappop, heappush
import time

def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """

    #priority heapqueue
    queue = []
    heappush(queue, (0, initial_position))

    came_from = dict()
    cost_so_far = dict()
    came_from[initial_position] = None
    cost_so_far[initial_position] = 0

    while len(queue):
        #grab current cost and current node
        current_cost, current_node = heappop(queue)

        # print("on node:", current_node)
        # print("current queue", queue)

        if cost_so_far[current_node] < current_cost:
            # print("duplicate")
            # print("duplicate node:", current_node)
            # print("cost on node:", cost_so_far[current_node])
            continue

        #stop if at the destination
        if current_node == destination:
            print("total cost:", cost_so_far[current_node])
            return reconstruct_path(came_from, initial_position, destination)
        else:
            #generate child nodes
            for new_node, new_cost in adj(graph, current_node):

                pathcost = current_cost + new_cost

                if new_node not in cost_so_far or pathcost < cost_so_far[new_node]:
                    cost_so_far[new_node] = pathcost

                    # print("pushing:", new_node)
                    # print("from: ", current_node)
                    # print("queue")
                    # print(queue)

                    heappush(queue, (pathcost, new_node))
                    came_from[new_node] = current_node

    return None

def reconstruct_path(came_from, initial_position, destination):

    current = destination
    path = []
    while current != initial_position:
        path.append(current)
        current = came_from[current]

    path.append(initial_position)

    return path

def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """

    # priority heapqueue
    queue = []
    heappush(queue, (0, initial_position))

    came_from = dict()
    cost_so_far = dict()
    came_from[initial_position] = None
    cost_so_far[initial_position] = 0

    while len(queue) > 0:
        # grab current cost and current node
        current_cost, current_node = heappop(queue)

        if cost_so_far[current_node] < current_cost:
            # print("duplicate")
            # print("duplicate node:", current_node)
            # print("cost on node:", cost_so_far[current_node])
            continue

        # generate child nodes
        for new_node, new_cost in adj(graph, current_node):
            pathcost = current_cost + new_cost

            if new_node not in cost_so_far or pathcost < cost_so_far[new_node]:
                cost_so_far[new_node] = pathcost

                heappush(queue, (pathcost, new_node))
                came_from[new_node] = current_node

    return cost_so_far

def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """

    adj_nodes = []

    #print("checking adj nodes for")
    #print(cell)

    for i in range(-1, 2):
        for j in range(-1, 2):
            new_cell = (cell[0]+i, cell[1]+j)
            #print("this is the new cell we be checking")
            #print(new_cell)
            #if not a wall and not the original cell
            if new_cell != cell and new_cell not in level["walls"]:
                #print("not a wall")
                #check if straight or diagonal and calculate distance
                if abs(i + j) == 1:
                    distance = 0.5 * level["spaces"][cell] + 0.5 * level["spaces"][new_cell]
                else:
                    distance = 0.5 * math.sqrt(2) * level["spaces"][cell] + 0.5 * math.sqrt(2) * level["spaces"][new_cell]

                new_tuple = (new_cell, distance)
                adj_nodes.append(new_tuple)

    #print("printing adj nodes")
    #print(adj_nodes)

    return adj_nodes

def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path)
    else:
        print("No path possible!")

def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]

    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)

if __name__ == '__main__':
    total_start = time.perf_counter()
    filename, src_waypoint, dst_waypoint = 'my_maze.txt', 'a','d'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_maze_costs.csv')
    print("Total Runtime: ", time.perf_counter() - total_start, " seconds")

