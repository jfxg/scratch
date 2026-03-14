"""
Game logic — absorption, board unlocking, win/loss detection.
All state mutations happen here. No pygame.

Absorption is modeled as continuous quantity flow:
  - Each box has 1.0 unit of material
  - Each ball holds up to 3.0 units (max_fill)
  - Each active slot drains its box at 1.0 unit/second
  - A ball greedily opens slots for every available matching column
  - The ball stops (and disappears) when fill >= max_fill
"""
from __future__ import annotations
from game.state import GameState, GameStatus, AbsorbingBall, AbsorptionSlot

EPS = 1e-9


def select_ball(state: GameState, row: int, col: int) -> bool:
    cell = state.board[row][col]
    if cell is None or cell.empty or not cell.unlocked:
        return False

    target_idx = next((i for i, b in enumerate(state.middle_row) if b is None), None)
    if target_idx is None:
        return False

    ball = AbsorbingBall(color=cell.color)
    state.middle_row[target_idx] = ball
    state.color_queues.setdefault(cell.color, []).append(target_idx)

    cell.empty = True
    _unlock_neighbours(state, row, col)
    return True


def _unlock_neighbours(state: GameState, row: int, col: int):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < state.board_rows and 0 <= nc < state.board_cols:
            neighbour = state.board[nr][nc]
            if neighbour is not None and not neighbour.empty:
                neighbour.unlocked = True
                if neighbour.hidden:
                    neighbour.hidden = False


def update(state: GameState, dt: float):
    if state.status != GameStatus.PLAYING:
        return

    for color, queue in state.color_queues.items():
        if not queue:
            continue
        idx = queue[0]
        ball = state.middle_row[idx]
        if ball is None:
            continue

        # Greedily open new slots for any matching column not already being drained
        if ball.remaining_capacity > EPS:
            _fill_slots(state, ball)

        # Drain all active slots
        completed_slots = []
        for slot in ball.slots:
            stack = state.stacks[slot.column]
            if not stack.colors:          # stack emptied by a previous slot this tick
                completed_slots.append(slot)
                continue
            drain = min(dt, stack.bottom_remaining, ball.remaining_capacity)
            stack.bottom_remaining -= drain
            ball.fill += drain

            if stack.bottom_remaining <= EPS:
                stack.pop_bottom()   # removes box, resets bottom_remaining to 1.0
                completed_slots.append(slot)

            if ball.remaining_capacity <= EPS:
                break   # ball is full mid-tick

        # Remove completed slots (box fully drained)
        for slot in completed_slots:
            ball.slots.remove(slot)

        # Fill any capacity freed by completed slots, or newly revealed boxes from
        # other balls that drained in this same tick.
        if ball.remaining_capacity > EPS:
            _fill_slots(state, ball)

        # Ball full: clear all remaining slots (partial boxes stay partially drained)
        if ball.remaining_capacity <= EPS:
            ball.fill = ball.max_fill
            ball.slots.clear()
            state.middle_row[idx] = None
            state.color_queues[color].pop(0)

    _check_end_conditions(state)


def _fill_slots(state: GameState, ball: AbsorbingBall):
    """Open slots for matching columns.
    - Empty ball (fill==0): absorb from all available columns simultaneously.
    - Non-empty ball: only start absorbing whole boxes. How many new slots we can
      open = floor(remaining_capacity - already_committed), where committed is the
      sum of bottom_remaining across all active slots (what they'll still drain).
      Minimum 1 if there's any capacity at all, so the ball never gets stuck.
    """
    if ball.remaining_capacity <= EPS:
        return

    if ball.fill == 0.0:
        can_add = len(state.stacks)  # unlimited for a fresh ball
    else:
        committed = sum(
            state.stacks[s.column].bottom_remaining
            for s in ball.slots
            if state.stacks[s.column].colors
        )
        available = ball.remaining_capacity - committed
        if available <= 0:
            return
        can_add = max(int(available), 1)  # at least 1 so the ball never stalls

    occupied = ball.active_columns
    for i, stack in enumerate(state.stacks):
        if can_add <= 0:
            break
        if i not in occupied and stack.bottom_color == ball.color:
            ball.slots.append(AbsorptionSlot(column=i))
            occupied.add(i)
            can_add -= 1


def _check_end_conditions(state: GameState):
    if state.total_remaining() < EPS:
        state.status = GameStatus.WON
        return

    if state.middle_row_full():
        bottom_colors = {s.bottom_color for s in state.stacks if s.bottom_color}
        active_colors = {b.color for b in state.middle_row if b is not None}
        if not active_colors.intersection(bottom_colors):
            state.status = GameStatus.LOST
