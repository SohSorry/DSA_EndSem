import time
from typing import List
from pathfinder.grid import Grid
from pathfinder.Astar import AStarPathfinder
from pathfinder.BFS import BFSPathfinder
from pathfinder.DFS import DFSPathfinder

class BenchmarkRunner:
    @staticmethod
    def run_benchmarks() -> None:
        print("Running Benchmarks...")
        
        # considerign size N = 10^3, 10^4, 10^5
        # grid dimensions approx can be : 32x32, 100x100, 316x316
        configs = [
            (32, 32, "10^3"),
            (100, 100, "10^4"),
            (316, 316, "10^5") 
        ]

        NUM_RUNS = 3

        for rows, cols, label in configs:
            print(f"\nSize: {label} nodes")
            
            # first making a setup for grid
            grid = Grid(rows, cols)
            grid.set_start((0, 0))
            grid.set_goal((rows-1, cols-1))
            
            # 1. for A*
            total_time = 0
            for _ in range(NUM_RUNS):
                start_t = time.time()
                astar = AStarPathfinder(grid)
                path = astar.find_path()
                total_time += (time.time() - start_t) * 1000
            avg_astar = total_time / NUM_RUNS
            print(f"A*: {avg_astar:.2f} ms")

            # 2. for BFS
            total_time = 0
            for _ in range(NUM_RUNS):
                start_t = time.time()
                bfs = BFSPathfinder(grid)
                path = bfs.find_path()
                total_time += (time.time() - start_t) * 1000
            avg_bfs = total_time / NUM_RUNS
            print(f"BFS: {avg_bfs:.2f} ms")

            # 3.for DFS
            # skipping DFS for largest set to avoid recursion depth issues or extreme slowness
            if rows <= 100:
                total_time = 0
                for _ in range(NUM_RUNS):
                    start_t = time.time()
                    dfs = DFSPathfinder(grid)
                    path = dfs.find_path()
                    total_time += (time.time() - start_t) * 1000
                avg_dfs = total_time / NUM_RUNS
                print(f"DFS: {avg_dfs:.2f} ms")
            else:
                print("DFS: Skipped")
            
        print("\nBenchmarks Completed.")