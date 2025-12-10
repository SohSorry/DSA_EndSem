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
