from typing import Tuple, Dict, List, Optional, Any
from pathfinder.node import Node

# grid class to manage the entire grid/graph of nodes
class Grid:
    # initialize grid with set number of rows and columns
    def __init__(self, rows: Optional[int] = None, cols: Optional[int] = None):
        # dict to store all nodes in the grid by position
        self.nodes: Dict[Tuple[int, int], Node] = {}

        # track start and goal positions
        self.start: Optional[Tuple[int, int]] = None
        self.goal: Optional[Tuple[int, int]] = None
        
        # store keys (waypoints) in order
        self.keys: List[Tuple[int, int]] = []

        # store barriers separately for quick lookup
        self.barriers: set[Tuple[int, int]] = set()

        # store grid dimensions if provided
        self.rows = rows
        self.cols = cols

        # auto-generate grid if dimensions provided
        if rows is not None and cols is not None:
            self._generate_grid(rows, cols)


    def add_node(self, pos: Tuple[int, int]) -> Node:
        node = Node(position=pos)
        self.nodes[pos] = node
        return node
    
    def _generate_grid(self, rows: int, cols: int): # regenerate grid
        for r in range(rows):
            for c in range(cols):
                self.add_node((r, c))


    # helper function to check if a node is available at a position
    def has_node(self, pos: Tuple[int, int]):
        return pos in self.nodes

    # helper function to get node at a position
    def get_node(self, pos: Tuple[int, int]):
        return self.nodes.get(pos)

    # set as starting point
    def set_start(self, pos: Tuple[int, int]):
        if pos not in self.nodes:
            return False
        self.start = pos
        return True

    # set as goal
    def set_goal(self, pos: Tuple[int, int]):
        if pos not in self.nodes:
            return False
        self.goal = pos
        return True

    def add_key(self, pos: Tuple[int, int]) -> bool:
        if pos not in self.nodes:
            return False
        if pos not in self.keys:
            self.keys.append(pos)
        return True

    def remove_key(self, pos: Tuple[int, int]) -> bool:
        if pos in self.keys:
            self.keys.remove(pos)
            return True
        return False

    def is_key(self, pos: Tuple[int, int]) -> bool:
        return pos in self.keys

    # add barrier at said position
    def add_barrier(self, pos: Tuple[int, int]):
        if pos not in self.nodes:
            return False
        self.barriers.add(pos)
        return True

    # remove barrier at said position
    def remove_barrier(self, pos: Tuple[int, int]):
        if pos in self.barriers:
            self.barriers.discard(pos)
            return True
        return False

    # check if position is a barrier
    def is_barrier(self, pos: Tuple[int, int]):
        return pos in self.barriers

    # check if position has a non-barrier node
    def is_valid(self, pos: Tuple[int, int]):
        return pos in self.nodes and pos not in self.barriers

    # get all neighbors in graph
    def get_neighbors(
            self,
            pos: Tuple[int, int],
    ) -> List[Node]:
        # extract row and column
        r, c = pos

        # 4-directional movement
        candidates = [
            (r - 1, c),  # up
            (r + 1, c),  # down
            (r, c - 1),  # left
            (r, c + 1),  # right
        ]

        # make sure returned nodes aren't barriers
        valid = [self.nodes[p] for p in candidates if self.is_valid(p)]
        return valid

    def reset_search(self): # reset all nodes for a fresh algorithm run
        for node in self.nodes.values():
            node.reset_search_state()