"""Random level generation — guaranteed solvable by construction."""
import random
from typing import Optional
from game.level_loader import build_state

ALL_COLORS = ["red", "green", "blue", "yellow", "purple", "cyan", "tan", "gray", "orange", "black"]


def generate_level(n_colors: int, board_w: int, board_h: int,
                   n_stacks: int = 4, seed: Optional[int] = None):
    if seed is None:
        seed = random.randint(0, 999_999)
    rng = random.Random(seed)

    colors = ALL_COLORS[:n_colors]
    total_cells = board_w * board_h

    # ── Step 1: pick N (divisible by 4, 50–75 % of board) ────────────────────
    lo = max(4, -(-total_cells * 50 // 100))   # ceil(50 %)
    hi = total_cells * 75 // 100               # floor(75 %)
    lo4 = -(-lo // 4) * 4                      # round lo up to nearest 4
    hi4 = (hi // 4) * 4                        # round hi down to nearest 4
    if lo4 > hi4:
        lo4 = hi4
    N = rng.choice(range(lo4, hi4 + 1, 4))

    max_stack_h = (N // 4) * 3   # per-stack height cap

    # ── Initialise stacks and board canvas ────────────────────────────────────
    stacks: list[list[str]] = [[] for _ in range(n_stacks)]
    cells: list[list[dict | None]] = [[None] * board_w for _ in range(board_h)]

    # Generation-phase unlock grid (separate from game unlock state)
    gen_unlocked = [[r == 0 for c in range(board_w)] for r in range(board_h)]
    placed: set[tuple[int, int]] = set()

    # ── Color bag: spread colors as evenly as possible across N placements ────
    base, extra = divmod(N, n_colors)
    color_bag: list[str] = colors * base + rng.sample(colors, extra)
    rng.shuffle(color_bag)

    # ── Steps 2–6: place balls and build stacks ───────────────────────────────
    for i in range(N):
        avail = [
            (r, c) for r in range(board_h) for c in range(board_w)
            if gen_unlocked[r][c] and (r, c) not in placed
        ]
        if not avail:
            break

        r, c = rng.choice(avail)
        color = color_bag[i]
        cells[r][c] = {"color": color}
        placed.add((r, c))

        # Add 3 boxes of this color to random non-full stacks
        non_full = [si for si in range(n_stacks) if len(stacks[si]) < max_stack_h]
        for _ in range(3):
            if not non_full:
                break
            si = rng.choice(non_full)
            stacks[si].append(color)
            if len(stacks[si]) >= max_stack_h:
                non_full.remove(si)

        # Unlock orthogonal neighbours
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < board_h and 0 <= nc < board_w:
                gen_unlocked[nr][nc] = True

    data = {
        "seed": seed,
        "columns": n_stacks,
        "middle_spaces": 7,
        "stacks": stacks,
        "board": {"rows": board_h, "cols": board_w, "cells": cells},
    }
    return build_state(data)
