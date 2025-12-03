from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Any, Dict, List

# ========================================= 1. SOHAIB =========================================


@dataclass(order=True) # in order to generate comparison methods
class Node:
    # node for grid pathfinding: stores position, A* costs (g,h,f), parent, visited flag, depth
    # f is first so heapq sorts by it automatically (A* priority queue)
    f: float = field(init=False, compare=True) # f, the sum of g and h
    position: Tuple[int, int] = field(compare=False) # (x, y) coords
    parent: Optional["Node"] = field(default=None, compare=False) # parent nodes for traversing tree
    g: float = field(default=0.0, compare=False) # cost 
    h: float = field(default=0.0, compare=False) # heuristic 
    visited: bool = field(default=False, compare=False)
    depth: int = field(default=0, compare=False)
    data: Any = field(default=None, compare=False)

    def _recalc_f(self) -> None: # calculate f
        self.f = self.g + self.h

    def __post_init__(self): # calculate f after initialization
        self._recalc_f()


    def reconstruct_path(self) -> List[Tuple[int, int]]: # walk back through parents to build path from start to this node
        path: List[Tuple[int, int]] = [] # to store path
        node: Optional[Node] = self
        while node is not None:
            path.append(node.position)
            node = node.parent
        path.reverse() # reverse to get path from start to goal
        return path

    def reset_search_state(self) -> None: # reset algorithm-specific state so node can be reused between runs
        self.parent = None
        self.g = 0.0
        self.h = 0.0
        self._recalc_f()
        self.visited = False
        self.depth = 0

