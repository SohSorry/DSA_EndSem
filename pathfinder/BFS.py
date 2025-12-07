from typing import Optional, List, Tuple, Set
from pathfinder.grid import Grid
from pathfinder.node import Node
from data_structures.queue import Queue

class BFSPathfinder:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.queue = Queue[Node]()
        self.visited: Set[Tuple[int, int]] = set()

    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        # check if start and goal are set
        if self.grid.start is None or self.grid.goal is None:
            print("Error: Start or goal not set!")
            return None

        # clear everything for a fresh search
        self.grid.reset_search()
        self.queue.clear()
        self.visited.clear()

        # add the start node to queue and mark as visited
        start_node = self.grid.get_node(self.grid.start)
        start_node.visited = True
        self.visited.add(start_node.position)
        self.queue.enqueue(start_node)

        nodes_explored = 0

        # keep exploring until queue is empty
        while not self.queue.is_empty():
            current = self.queue.dequeue()
            nodes_explored += 1

            # check if we reached the goal
            if current.position == self.grid.goal:
                path = current.reconstruct_path()
                print(f"BFS Path found. Length: {len(path)}, Nodes explored: {nodes_explored}")
                return path

            # add all unvisited neighbors to queue
            for neighbor in self.grid.get_neighbors(current.position):
                if neighbor.position not in self.visited:
                    self.visited.add(neighbor.position)
                    neighbor.parent = current
                    neighbor.visited = True
                    neighbor.depth = current.depth + 1
                    self.queue.enqueue(neighbor)

        print(f"BFS: No path found. Nodes explored: {nodes_explored}")
        return None