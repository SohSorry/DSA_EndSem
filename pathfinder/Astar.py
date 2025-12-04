from typing import Optional, List, Tuple, Callable
from pathfinder.grid import Grid
from pathfinder.node import Node
from data_structures.min_heap import MinHeap
class AStarPathfinder:

    def __init__(
            self,
            grid: Grid,
            # the cost function simply returns a float value that determines cost of going from one node to another
            cost_function: Optional[Callable[[Node, Node], float]] = None
    ):
        self.grid = grid # the grid to search on
        self.open_set = MinHeap[Node]() # priority queue for open set
        self.closed_set: set[Tuple[int, int]] = set() # set of visited positions

        # default cost function: constant 1.0
        if cost_function is None:
            self.cost_function = lambda n1, n2: 1.0
        else:
            self.cost_function = cost_function

        # default heuristic: Manhattan distance
        self.heuristic_function = self._manhattan_distance

    def _manhattan_distance(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        if self.grid.start is None or self.grid.goal is None:
            print("Error: Start or goal not set!")
            return None

        full_path = []
        nodes_explored_total = 0
        
        # define waypoints: start, keys, goal
        waypoints = [self.grid.start] + self.grid.keys + [self.grid.goal]
        
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i+1]
            
            segment, explored = self._find_segment(start, end)
            nodes_explored_total += explored
            
            if segment is None:
                print(f"A*: No path found between {start} and {end}")
                return None
                
            # if this is not the first segment, remove the first node (duplicate of previous segment's last node)
            if i > 0:
                segment = segment[1:]
                
            full_path.extend(segment)
            
        print(f"A* Path found. Total Length: {len(full_path)}, Total Nodes Explored: {nodes_explored_total}")
        return full_path

    def _find_segment(self, start_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> Tuple[Optional[List[Tuple[int, int]]], int]:
        # reset grid for fresh search
        self.grid.reset_search()
        self.open_set = MinHeap[Node]()
        self.closed_set = set()

        # initialize start node
        start_node = self.grid.get_node(start_pos)
        start_node.g = 0
        start_node.h = self.heuristic_function(start_pos, goal_pos)
        start_node._recalc_f()

        # add start to open set
        self.open_set.push(start_node)

        nodes_explored = 0

        # main A* loop
        while not self.open_set.is_empty():
            current = self.open_set.pop()
            nodes_explored += 1

            # skip if already visited
            if current.position in self.closed_set:
                continue

            # mark as visited
            self.closed_set.add(current.position)
            current.visited = True

            # check if we reached the goal
            if current.position == goal_pos:
                path = current.reconstruct_path()
                return path, nodes_explored

            # explore neighbors
            neighbors = self.grid.get_neighbors(current.position)

            for neighbor in neighbors:
                # skip if already visited
                if neighbor.position in self.closed_set:
                    continue

                # calculate cost to move from current to neighbor
                move_cost = self.cost_function(current, neighbor)

                # calculate tentative g cost
                tentative_g = current.g + move_cost

                # if this path to neighbor is better than any previous one
                if tentative_g < neighbor.g or neighbor.g == 0:
                    # update neighbor
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic_function(neighbor.position, goal_pos)
                    neighbor.depth = current.depth + 1
                    neighbor._recalc_f()

                    # add to open set
                    self.open_set.push(neighbor)

        return None, nodes_explored





