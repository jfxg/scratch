## Stack Absorber — Puzzle Game

### Game Description

A real-time puzzle game where the player strategically deploys colored balls to absorb matching colored boxes from stacks. Timing and sequencing are critical — *when* you place a ball can determine whether the puzzle is solvable.

---

### Screen Layout

**Top — Box Stacks**
- 4 columns of colored boxes (default; configurable via `--stacks`)
- Only the bottom 7 are visible at any time
- The player cannot interact with the stacks directly

**Middle — Absorption Row**
- 7 spaces where active balls sit and absorb boxes
- Balls absorb boxes whose color matches their own, from any column simultaneously
- Only one ball of a given color may absorb at a time; if two balls share a color, the one placed first absorbs until full, then the next begins
- A ball can hold up to 3 units of material (one unit per box); it disappears when full
- Balls absorb simultaneously across colors (e.g. a red ball and a blue ball both absorb at the same time)
- Once a ball is placed on the middle row, it cannot be moved or removed by the player

**Bottom — Player Board**
- A grid of colored balls that changes shape each level (some cells are blocked/deactivated)
- Only the top row of the board is accessible at the start
- Clicking a ball removes it from the board and sends it to the leftmost available space on the middle row, where it immediately begins absorbing
- When a ball is removed from the board, all orthogonally adjacent cells (up/down/left/right) are immediately unlocked
- Some balls may have their color hidden; the color is revealed when the cell is unlocked by removing an adjacent ball

---

### Absorption Mechanics

Absorption is modeled as continuous quantity flow:

- Each box contains **1.0 unit** of material; each ball holds up to **3.0 units**
- Each active absorption slot drains its box at **1.0 unit/second**
- A **fresh ball** (empty, fill = 0) opens slots for **all** matching columns simultaneously — no matter how many
- A **partially filled ball** opens slots for whole boxes only: up to `floor(remaining_capacity − already_committed)` new slots, minimum 1 (so the ball never stalls)
- As a bottom box is absorbed, it shrinks in real-time; the stack above it lowers at the same rate (smooth animation)
- When a box finishes draining, the next box in the stack becomes available immediately
- If a new matching box appears mid-tick (e.g. revealed by another ball), the absorbing ball picks it up immediately if it has capacity

---

### Win / Loss Conditions

- **Win**: All boxes in all stacks are cleared
- **Lose (Deadlock)**: All middle-row spaces are occupied by balls, but none of the balls match the color of any box at the bottom of any stack

---

### Running the Game

```bash
# Random level with default settings
python main.py

# Random level with custom settings
python main.py --colors 7 --board 6x5 --stacks 4

# Replay a specific generated level by seed
python main.py --seed 42

# Load a hand-crafted level from JSON
python main.py level.json
```

Press **R** to restart / generate a new level at any time.

The seed ID for generated levels is shown in the bottom-right corner so you can replay them with `--seed`.

---

### Level Format (JSON)

```json
{
  "columns": 4,
  "middle_spaces": 7,
  "stacks": [
    ["red", "blue", "red"],
    ["blue", "green", "blue"],
    ["green", "red", "green"],
    ["red", "blue", "green"]
  ],
  "board": {
    "rows": 3,
    "cols": 4,
    "cells": [
      [{"color": "red"}, {"color": "blue"}, null, {"color": "green"}],
      [{"color": "red", "hidden": true}, null, {"color": "blue"}, {"color": "green"}],
      [null, {"color": "red"}, {"color": "blue"}, null]
    ]
  }
}
```

- Supported colors: `red`, `green`, `blue`, `yellow`, `purple`, `cyan`, `tan`, `gray`, `orange`, `black`
- `stacks`: Each array lists box colors from **bottom to top**
- `cells`: Each object is an active cell with a `color` and optional `"hidden": true`; `null` means the cell is blocked/deactivated
- The top row of `cells` is the only row accessible at game start

---

### Random Level Generation

Levels are generated to be solvable by construction:

1. Pick N board cells to fill (a random multiple of 4, between 50–75% of the board)
2. Place balls on the board using the same unlock rules as the game (top row first, then adjacency)
3. For each placed ball, add 3 matching boxes distributed randomly across the stacks
4. Total box material = N × 3 = total ball capacity → guaranteed balanced

The `--colors` flag controls how many distinct colors appear (1–10). The `--board WxH` flag sets board dimensions. The `--stacks` flag sets the number of stack columns.

---

### Architecture

```
main.py                # Entry point — CLI args, pygame loop, event handling
game/
  state.py             # Pure game state: stacks, middle row, board, absorption queues
  mechanics.py         # All game logic: absorption, unlock, win/loss detection
  renderer.py          # All pygame drawing — no game logic
  level_loader.py      # Parses JSON level dict/file into GameState
  level_generator.py   # Random solvable level generation
```

Game state is kept strictly separate from rendering so a solver can operate directly on state without any graphics dependency.

---

### Planned Features

- [x] Level loading from JSON
- [x] Random level generation with seed replay
- [x] Rendering: stacks, middle row, player board
- [x] Click interaction and middle row ball placement
- [x] Real-time absorption with smooth stack-lowering animation
- [x] Win/loss detection
- [ ] Solver: finds optimal move sequence given a level
