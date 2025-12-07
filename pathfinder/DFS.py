from typing import Optional, List, Tuple, Set
from pathfinder.grid import Grid
from pathfinder.node import Node
from data_structures.stack import Stack


class DFSPathfinder:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.stack = Stack[Node]()
        self.visited: Set[Tuple[int, int]] = set()

    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        if self.grid.start is None or self.grid.goal is None:
            print("Error: Start or goal not set!")
            return None

        # Reset grid state
        self.grid.reset_search()
        self.stack.clear()
        self.visited.clear()

        start_node = self.grid.get_node(self.grid.start)
        self.stack.push(start_node)

        nodes_explored = 0

        while not self.stack.is_empty():
            current = self.stack.pop()

            if current.position in self.visited:
                continue

            self.visited.add(current.position)
            current.visited = True
            nodes_explored += 1

            if current.position == self.grid.goal:
                path = current.reconstruct_path()
                print(f"DFS Path found. Length: {len(path)}, Nodes explored: {nodes_explored}")
                return path

            # Get neighbors
            neighbors = self.grid.get_neighbors(current.position)

            # Note: Iterating in reverse order ensures the first neighbor 
            # is popped first from the stack (optional optimization for visuals)
            for neighbor in neighbors:
                if neighbor.position not in self.visited:
                    neighbor.parent = current
                    self.stack.push(neighbor)

        print(f"DFS: No path found. Nodes explored: {nodes_explored}")
        return None