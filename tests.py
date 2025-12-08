import time
from typing import List, Tuple, Optional
from pathfinder.grid import Grid
from pathfinder.Astar import AStarPathfinder
from pathfinder.BFS import BFSPathfinder
from pathfinder.DFS import DFSPathfinder
from pathfinder.node import Node

class TestRunner:
    @staticmethod
    def run_all_tests() -> None:
        print("Running Validation Tests...")

        # Test 1: Simple Path
        if TestRunner._test_simple_path():
            print("Test 1 (Simple Path): PASS")
        else:
            print("Test 1 (Simple Path): FAIL")

        # Test 2: Barrier Block
        if TestRunner._test_barrier_block():
            print("Test 2 (Barrier Block): PASS")
        else:
            print("Test 2 (Barrier Block): FAIL")

        # Test 3: Start == Goal
        if TestRunner._test_start_is_goal():
            print("Test 3 (Start=Goal): PASS")
        else:
            print("Test 3 (Start=Goal): FAIL")

        # Test 4: Complex Maze
        if TestRunner._test_complex_maze():
            print("Test 4 (Complex Maze): PASS")
        else:
            print("Test 4 (Complex Maze): FAIL")

        # Test 5: Optimality Check
        if TestRunner._test_optimality():
            print("Test 5 (Optimality): PASS")
        else:
            print("Test 5 (Optimality): FAIL")
            
        print("Tests Completed.")

    @staticmethod
    def _validate_path(path: List[Tuple[int, int]], grid: Grid) -> bool:
        if not path:
            return False
        
        # Check start and end
        if path[0] != grid.start:
            print(f"    Invalid start: {path[0]} != {grid.start}")
            return False
        if path[-1] != grid.goal:
            print(f"    Invalid goal: {path[-1]} != {grid.goal}")
            return False
            
        # Check continuity and barriers
        for i in range(len(path) - 1):
            curr = path[i]
            next_node = path[i+1]
            
            # Check if neighbors (Manhattan distance 1)
            dist = abs(curr[0] - next_node[0]) + abs(curr[1] - next_node[1])
            if dist != 1:
                print(f"    Discontinuity: {curr} -> {next_node}")
                return False
                
            # Check barriers
            if grid.is_barrier(curr) or grid.is_barrier(next_node):
                print(f"    Path goes through barrier: {curr} or {next_node}")
                return False
                
        return True

    @staticmethod
    def _test_simple_path() -> bool:
        # 10x10 grid, start (0,0), goal (9,9)
        grid = Grid(10, 10)
        grid.set_start((0, 0))
        grid.set_goal((9, 9))
        
        # test a* pathfinder
        astar = AStarPathfinder(grid)
        p1 = astar.find_path()
        if not p1 or not TestRunner._validate_path(p1, grid):
            print("    A* failed")
            return False
        
        # test bfs pathfinder
        bfs = BFSPathfinder(grid)
        p2 = bfs.find_path()
        if not p2 or not TestRunner._validate_path(p2, grid):
            print("    BFS failed")
            return False
        
        # test dfs pathfinder
        dfs = DFSPathfinder(grid)
        p3 = dfs.find_path()
        if not p3 or not TestRunner._validate_path(p3, grid):
            print("    DFS failed")
            return False
        
        return True

    @staticmethod
    def _test_barrier_block() -> bool:
        # 5x5 grid, wall in middle
        grid = Grid(5, 5)
        grid.set_start((0, 0))
        grid.set_goal((0, 4))
        
        # block col 2 to create barrier
        for r in range(5):
            grid.add_barrier((r, 2))
            
        # both algorithms should return none (no path exists)
        astar = AStarPathfinder(grid)
        p1 = astar.find_path()
        
        bfs = BFSPathfinder(grid)
        p2 = bfs.find_path()
        
        return p1 is None and p2 is None