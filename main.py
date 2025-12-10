import pygame
import sys
import math
import time
import os
from typing import Tuple, Optional, List, Dict
from pathfinder.grid import Grid
from pathfinder.node import Node
from pathfinder.Astar import AStarPathfinder
from pathfinder.BFS import BFSPathfinder
from pathfinder.DFS import DFSPathfinder
from game import Terrain
from tests import TestRunner
from benchmark import BenchmarkRunner

# screen and grid dimensions
SCREEN_WIDTH = 1150
SCREEN_HEIGHT = 700
GRID_AREA_SIZE = 700
SIDEBAR_WIDTH = SCREEN_WIDTH - GRID_AREA_SIZE

ROWS = 22
COLS = 22
CELL_SIZE = 32

# colors for various elements
COLORS = {
    "BG": (250, 248, 245),
    "GRID_LINE": (230, 230, 230),
    "TEXT": (60, 60, 60),
    "BARRIER": (45, 52, 54),
    "EMPTY": (255, 255, 255),
    "START": (255, 107, 107),
    "GOAL": (78, 205, 196),
    "KEY": (255, 215, 0), # gold
    "PATH": (255, 217, 61),
    "EXPLORED": (220, 240, 255),

    "PLAIN": (223, 230, 233),
    "GRASS": (186, 220, 88),
    "ICE": (200, 240, 255),
    "DESERT": (240, 230, 140),
    "MUD": (139, 69, 19),

    "BTN_IDLE": (225, 225, 225),
    "BTN_HOVER": (200, 200, 200),
}

# load tile images from the tiles folder
def load_tile_image(name: str) -> Optional[pygame.Surface]:
    path = os.path.join("tiles", name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except pygame.error:
            print(f"Warning: Could not load image {path}")
            return None
    return None

# button class for ui elements
class Button:
    def __init__(self, x, y, w, h, text, action, color=COLORS["BTN_IDLE"], text_color=COLORS["TEXT"]):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.base_color = color
        self.text_color = text_color
        self.hovered = False
        self.click_anim = 0  # animation counter for button press effect

    def draw(self, surface, font):
        # shrink button slightly when clicked for visual feedback
        draw_rect = self.rect.inflate(-2, -2) if self.click_anim > 0 else self.rect
        if self.click_anim > 0: self.click_anim -= 1

        # change color on hover
        color = COLORS["BTN_HOVER"] if self.hovered else self.base_color
        pygame.draw.rect(surface, color, draw_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["TEXT"], draw_rect, 2, border_radius=8)

        # render and center the button text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # check if mouse is hovering over button
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # trigger action on left click
            if self.hovered and event.button == 1:
                self.click_anim = 5
                self.action()
    # main application class         
class VisualizerApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pathfinder Simulator")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 14, bold=True)

        self.grid = Grid(ROWS, COLS)
        self.initialize_barriers()

        # load Images
        self.images = {
            "PLAIN": load_tile_image("plain.png"),
            "GRASS": load_tile_image("grass.png"),
            "ICE": load_tile_image("ice.png"),
            "DESERT": load_tile_image("desert.png"),
            "MUD": load_tile_image("mud.png"),
            "BARRIER": load_tile_image("barrier.png")
        }

        # state of game
        self.current_tool = "BARRIER"
        self.selected_terrain = None

        self.path: List[Tuple[int, int]] = []

        # animation state
        self.tile_anims: Dict[Tuple[int, int], float] = {}  # (r,c) -> scale (0.0 to 1.0)
        self.path_draw_progress = 0.0  # how many path nodes to draw

        self.buttons = []
        self.setup_ui()

    def initialize_barriers(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.grid.add_barrier((r, c))
                if not self.grid.has_node((r, c)):
                    self.grid.add_node((r, c))

    def setup_ui(self):
        x_start, y, w, h, gap = GRID_AREA_SIZE + 20, 20, 120, 35, 8

        def set_tool(tool, terrain=None):
            self.current_tool = tool
            self.selected_terrain = terrain
            t_name = terrain.name if terrain else tool
            print(f"Tool selected: {t_name}")

        # control Buttons
        self.buttons.append(Button(x_start, y, w, h, "Start Point", lambda: set_tool("START"), COLORS["START"]))
        self.buttons.append(Button(x_start + w + gap, y, w, h, "Goal Point", lambda: set_tool("GOAL"), COLORS["GOAL"]))
        y += h + gap
        self.buttons.append(Button(x_start, y, w * 2 + gap, h, "Add Key", lambda: set_tool("KEY"), COLORS["KEY"]))
        y += h + gap
        self.buttons.append(
            Button(x_start, y, w * 2 + gap, h, "Barrier (∞)", lambda: set_tool("BARRIER"), COLORS["BARRIER"], text_color=(255, 255, 255)))
        y += h + gap + 5

        # terrain Buttons
        terrain_map = {
            Terrain.PLAIN: COLORS["PLAIN"],
            Terrain.GRASS: COLORS["GRASS"],
            Terrain.ICE: COLORS["ICE"],
            Terrain.DESERT: COLORS["DESERT"],
            Terrain.MUD: COLORS["MUD"]
        }

        for t, col in terrain_map.items():
            btn = Button(x_start, y, w * 2 + gap, 28, f"{t.name} ({int(t.value)})", lambda t=t: set_tool("TERRAIN", t), col)
            self.buttons.append(btn)
            y += 32

        y += 10
        # algorithm Buttons
        algos = [("Run A*", "ASTAR", (255, 200, 100)), ("Run BFS", "BFS", (200, 200, 255)),
                 ("Run DFS", "DFS", (255, 200, 200))]
        for label, key, col in algos:
            self.buttons.append(Button(x_start, y, w * 2 + gap, h, label, lambda k=key: self.run_algorithm(k), col))
            y += h + gap

        y += 5
        self.buttons.append(Button(x_start, y, w, h, "Clear Path", self.clear_path))
        self.buttons.append(Button(x_start + w + gap, y, w, h, "Reset All", self.reset_grid))

        y += h + gap + 5
        # validation & Benchmark Buttons
        self.buttons.append(Button(x_start, y, w, h, "Run Tests", self.run_tests, (200, 230, 200)))
        self.buttons.append(Button(x_start + w + gap, y, w, h, "Benchmark", self.run_benchmark, (230, 200, 230)))
        
        # storing the final Y for stats positioning
        self.stats_y_start = y + h + 20

    def run_tests(self):
        TestRunner.run_all_tests()

    def run_benchmark(self):
        BenchmarkRunner.run_benchmarks()

    def run_algorithm(self, algo_type):
        if not self.grid.start or not self.grid.goal:
            print("Set Start/Goal first!")
            return