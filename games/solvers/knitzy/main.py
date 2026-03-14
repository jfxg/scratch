#!/usr/bin/env python3
"""
Stack Absorber — entry point.

Usage:
  python main.py                          # random level, default settings
  python main.py --colors 7 --board 6x5  # random level, custom settings
  python main.py --seed 42               # replay a specific generated level
  python main.py level.json              # load a hand-crafted level file
"""
import sys
import argparse
import pygame
from game.level_loader import load_level
from game.level_generator import generate_level
from game.mechanics import update, select_ball
from game.renderer import Renderer
from game.state import GameStatus

FPS = 60
WINDOW_W = 900
WINDOW_H = 820


def parse_args():
    p = argparse.ArgumentParser(description="Stack Absorber puzzle game")
    p.add_argument("level", nargs="?", help="Path to a JSON level file (skips generation)")
    p.add_argument("--colors", type=int, default=9,
                   help="Number of colors for generated level (default: 9, max: 10)")
    p.add_argument("--stacks", type=int, default=4,
                   help="Number of stack columns (default: 4)")
    p.add_argument("--board", default="8x6", metavar="WxH",
                   help="Board dimensions for generated level (default: 8x6)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed — replay a specific generated level")
    return p.parse_args()


def main():
    args = parse_args()

    # Validate
    args.colors = max(1, min(10, args.colors))
    try:
        bw, bh = map(int, args.board.lower().split("x"))
    except ValueError:
        print(f"Invalid --board format '{args.board}'. Use WxH, e.g. 8x6.")
        sys.exit(1)

    def load_state():
        if args.level:
            return load_level(args.level)
        return generate_level(args.colors, bw, bh, args.stacks, args.seed)

    state = load_state()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Stack Absorber")
    clock = pygame.time.Clock()
    renderer = Renderer(screen, state)
    hovered_cell = None

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = load_state()
                    renderer = Renderer(screen, state)
                    hovered_cell = None

            if event.type == pygame.MOUSEMOTION:
                hovered_cell = renderer.cell_at(*event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = renderer.cell_at(*event.pos)
                if cell is not None and state.status == GameStatus.PLAYING:
                    select_ball(state, cell[0], cell[1])

        if state.status == GameStatus.PLAYING:
            update(state, dt)

        renderer.draw(hovered_cell)


if __name__ == "__main__":
    main()
