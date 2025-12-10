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
from tests import TestRunner
from benchmark import BenchmarkRunner
from enum import Enum

class Terrain(Enum):
    """Terrain types with associated movement costs."""
    PLAIN = 1.0
    GRASS = 2.0
    ICE = 4.0
    DESERT = 8.0
    MUD = 10.0




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

        self.clear_path()

        finder = None
        start_time = time.time()

        if algo_type == "ASTAR":
            def terrain_cost(n1, n2):
                return n2.data.value if isinstance(n2.data, Terrain) else 1.0

            finder = AStarPathfinder(self.grid, cost_function=terrain_cost)
            print(f"Algorithm: A* (A-Star)")
        elif algo_type == "BFS":
            finder = BFSPathfinder(self.grid)
            print(f"Algorithm: Breadth-First Search")
        elif algo_type == "DFS":
            finder = DFSPathfinder(self.grid)
            print(f"Algorithm: Depth-First Search")

        if finder:
            self.path = finder.find_path() or []
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            if self.path:
                exp = sum(1 for n in self.grid.nodes.values() if n.visited)
                print(f"Time: {duration_ms:.2f} ms")
                print(f"Path Length: {len(self.path)}")
                print(f"Nodes Explored: {exp}")

                if algo_type == "ASTAR":
                    total_cost = 0
                    for i in range(len(self.path) - 1):
                        n2 = self.grid.get_node(self.path[i + 1])
                        cost = n2.data.value if isinstance(n2.data, Terrain) else 1.0
                        total_cost += cost
                    print(f"Total Path Cost: {total_cost}")

                self.path_draw_progress = 0.0  # Reset animation
            else:
                print("Result: No Path Found")
                print(f"Time: {duration_ms:.2f} ms")


    def clear_path(self):
        self.path = []
        self.path_draw_progress = 0.0
        self.grid.reset_search()
        print("Path cleared.")


    def reset_grid(self):
        self.clear_path()
        self.grid.start = None
        self.grid.goal = None
        self.grid.keys.clear()
        self.initialize_barriers()
        self.tile_anims.clear()
        print("Map reset.")


    def handle_grid_click(self, pos):
        c, r = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
        if not (0 <= r < ROWS and 0 <= c < COLS): return

        grid_pos = (r, c)
        mouse_btns = pygame.mouse.get_pressed()

        changed = False

        if mouse_btns[0]:  # Draw
            if self.current_tool == "BARRIER":
                if not self.grid.is_barrier(grid_pos):
                    self.grid.add_barrier(grid_pos)
                    changed = True
                    if self.grid.start == grid_pos: self.grid.start = None
                    if self.grid.goal == grid_pos: self.grid.goal = None
            elif self.current_tool in ["START", "GOAL", "KEY"]:
                self.grid.remove_barrier(grid_pos)
                # Ensure underlying node data exists
                if self.grid.get_node(grid_pos).data is None:
                    # Default to PLAIN
                    default = Terrain.PLAIN
                    self.grid.get_node(grid_pos).data = default

                if self.current_tool == "START":
                    self.grid.set_start(grid_pos)
                elif self.current_tool == "GOAL":
                    self.grid.set_goal(grid_pos)
                elif self.current_tool == "KEY":
                    self.grid.add_key(grid_pos)
                changed = True
            elif self.current_tool == "TERRAIN":
                self.grid.remove_barrier(grid_pos)
                if not self.grid.has_node(grid_pos): self.grid.add_node(grid_pos)
                self.grid.get_node(grid_pos).data = self.selected_terrain
                changed = True

        elif mouse_btns[2]:  # Erase / Right Click
            self.grid.remove_barrier(grid_pos)
            self.grid.remove_key(grid_pos)
            if self.grid.has_node(grid_pos):
                default = Terrain.PLAIN
                self.grid.get_node(grid_pos).data = default
                changed = True

        # Trigger Pop Animation if changed
        if changed:
            self.tile_anims[grid_pos] = 0.1


    def draw_grid(self):
        # Time for bobbing animations
        ticks = pygame.time.get_ticks()
        bob_offset = math.sin(ticks * 0.005) * 3  # +/- 3 pixels

        for r in range(ROWS):
            for c in range(COLS):
                pos = (r, c)
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                # 1. Determine Base Color / Image
                color = COLORS["EMPTY"]
                image = None
                node = self.grid.get_node(pos)

                if self.grid.is_barrier(pos):
                    image = self.images.get("BARRIER")
                    color = COLORS["BARRIER"]
                elif node and isinstance(node.data, Terrain):
                    key = node.data.name
                    image = self.images.get(key)
                    # Fallback colors if image fails
                    if key == "PLAIN":
                        color = COLORS.get("ROAD", (223, 230, 233))
                    elif key == "GRASS":
                        color = COLORS["GRASS"]
                    elif key == "ICE":
                        color = (200, 240, 255)
                    elif key == "DESERT":
                        color = (240, 230, 140)
                    elif key == "MUD":
                        color = (139, 69, 19)

                # 2. Handle Tile Pop Animation
                draw_rect = rect
                if pos in self.tile_anims:
                    scale = self.tile_anims[pos]
                    # Grow animation
                    if scale < 1.0:
                        self.tile_anims[pos] += 0.1
                        center = rect.center
                        w = int(CELL_SIZE * scale)
                        h = int(CELL_SIZE * scale)
                        draw_rect = pygame.Rect(0, 0, w, h)
                        draw_rect.center = center
                    else:
                        del self.tile_anims[pos]  # Animation done

                if image:
                    # Scale image if animating
                    if draw_rect != rect:
                        scaled_img = pygame.transform.scale(image, (draw_rect.width, draw_rect.height))
                        self.screen.blit(scaled_img, draw_rect)
                    else:
                        self.screen.blit(image, draw_rect)
                else:
                    pygame.draw.rect(self.screen, color, draw_rect, border_radius=4)

                # 3. Explored Overlay (Subtle)
                if node and node.visited and pos not in self.path:
                    # Small circle instead of full rect for cuteness
                    pygame.draw.circle(self.screen, COLORS["EXPLORED"], rect.center, 4)

        # 4. Draw Path (Snake Animation)
        if self.path:
            # Increase progress
            if self.path_draw_progress < len(self.path):
                self.path_draw_progress += 0.5  # Speed of snake

            visible_count = int(self.path_draw_progress)
            for i in range(visible_count):
                p = self.path[i]
                rect = pygame.Rect(p[1] * CELL_SIZE, p[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                # Draw path as rounded connectors
                inner = rect.inflate(-12, -12)
                pygame.draw.rect(self.screen, COLORS["PATH"], inner, border_radius=5)

                # Connect visual to previous node for smooth look
                if i > 0:
                    prev = self.path[i - 1]
                    # Draw line between centers
                    start_center = (prev[1] * CELL_SIZE + CELL_SIZE // 2, prev[0] * CELL_SIZE + CELL_SIZE // 2)
                    end_center = (p[1] * CELL_SIZE + CELL_SIZE // 2, p[0] * CELL_SIZE + CELL_SIZE // 2)
                    pygame.draw.line(self.screen, COLORS["PATH"], start_center, end_center, 8)

        # 5. Draw Start/Goal (On top)
        def draw_marker(pos, color, letter):
            base_rect = pygame.Rect(pos[1] * CELL_SIZE, pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Main Body
            body = base_rect.inflate(-6, -6)
            pygame.draw.rect(self.screen, color, body, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), body, 2, border_radius=8)

            # Text
            txt = self.small_font.render(letter, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=body.center))

        if self.grid.start: draw_marker(self.grid.start, COLORS["START"], "S")
        if self.grid.goal: draw_marker(self.grid.goal, COLORS["GOAL"], "G")

        # Draw Keys
        for i, key_pos in enumerate(self.grid.keys):
            draw_marker(key_pos, COLORS["KEY"], str(i + 1))

        # Grid Lines (Subtle)
        for r in range(ROWS + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (0, r * CELL_SIZE), (GRID_AREA_SIZE, r * CELL_SIZE))
        for c in range(COLS + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (c * CELL_SIZE, 0), (c * CELL_SIZE, GRID_AREA_SIZE))


    def draw_sidebar(self):
        rect = pygame.Rect(GRID_AREA_SIZE, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (245, 245, 250), rect)
        pygame.draw.line(self.screen, (220, 220, 220), (GRID_AREA_SIZE, 0), (GRID_AREA_SIZE, SCREEN_HEIGHT), 2)

        for btn in self.buttons: btn.draw(self.screen, self.font)


    def run(self):
        while True:
            self.screen.fill(COLORS["BG"])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for btn in self.buttons: btn.handle_event(event)

            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_AREA_SIZE:
                    self.handle_grid_click(pos)

            self.draw_grid()
            self.draw_sidebar()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    VisualizerApp().run()