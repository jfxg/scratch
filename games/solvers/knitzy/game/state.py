"""
Pure game state — no pygame, no rendering.
All times are in seconds (floats).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class GameStatus(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class BoxStack:
    """One column of colored boxes. Index 0 = bottom."""
    colors: list[str]           # bottom → top
    bottom_remaining: float = 1.0   # quantity remaining in bottom box (0.0 → 1.0)

    def __len__(self):
        return len(self.colors)

    @property
    def bottom_color(self) -> Optional[str]:
        return self.colors[0] if self.colors else None

    def pop_bottom(self):
        """Remove fully-drained bottom box; reset remaining for new bottom."""
        self.colors.pop(0)
        self.bottom_remaining = 1.0

    @property
    def absorb_progress(self) -> float:
        """How far along the current bottom box is being drained (0.0 → 1.0)."""
        return 1.0 - self.bottom_remaining


@dataclass
class AbsorptionSlot:
    """One independent drain channel on a ball, targeting one stack column."""
    column: int


@dataclass
class AbsorbingBall:
    """A ball sitting on the middle row, filling up as it absorbs boxes."""
    color: str
    fill: float = 0.0       # units absorbed so far
    max_fill: float = 3.0   # capacity in units (= 3 full boxes)
    slots: list[AbsorptionSlot] = field(default_factory=list)

    @property
    def active_columns(self) -> set[int]:
        return {s.column for s in self.slots}

    @property
    def fill_fraction(self) -> float:
        """0.0 = empty, 1.0 = full."""
        return min(self.fill / self.max_fill, 1.0)

    @property
    def remaining_capacity(self) -> float:
        return max(0.0, self.max_fill - self.fill)

    @property
    def free_slots(self) -> int:
        """How many more simultaneous absorptions this ball can start."""
        # capacity in whole boxes minus currently active slots
        return max(0, int(self.remaining_capacity // 1 + (1 if self.remaining_capacity % 1 > 1e-9 else 0)) - len(self.slots))


@dataclass
class BoardCell:
    color: str
    hidden: bool = False
    unlocked: bool = False
    empty: bool = False


@dataclass
class GameState:
    stacks: list[BoxStack]
    middle_spaces: int
    middle_row: list[Optional[AbsorbingBall]]
    board: list[list[Optional[BoardCell]]]
    status: GameStatus = GameStatus.PLAYING
    seed: Optional[int] = None

    # Per-color FIFO queue: color → list of middle-row indices (placement order)
    color_queues: dict[str, list[int]] = field(default_factory=dict)

    @property
    def board_rows(self) -> int:
        return len(self.board)

    @property
    def board_cols(self) -> int:
        return len(self.board[0]) if self.board else 0

    def middle_row_full(self) -> bool:
        return all(b is not None for b in self.middle_row)

    def total_remaining(self) -> float:
        """Total units of boxes still in stacks (including partially drained)."""
        total = 0.0
        for s in self.stacks:
            if not s.colors:
                continue
            total += s.bottom_remaining + max(0, len(s) - 1)
        return total
