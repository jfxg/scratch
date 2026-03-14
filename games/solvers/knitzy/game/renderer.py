"""
All pygame drawing. No game logic.
"""
from __future__ import annotations
import math
import pygame
from game.state import GameState, GameStatus

# ── Palette ───────────────────────────────────────────────────────────────────
BG_COLOR      = (18, 18, 30)
GRID_COLOR    = (50, 50, 70)
LOCKED_COLOR  = (35, 35, 50)
EMPTY_COLOR   = (25, 25, 40)
BLOCKED_COLOR = (12, 12, 20)
TEXT_COLOR    = (220, 220, 240)
MIDDLE_BG     = (28, 28, 45)
HIDDEN_COLOR  = (70, 70, 90)

BALL_COLORS: dict[str, tuple[int,int,int]] = {
    "red":    (220,  55,  55),
    "green":  ( 55, 195,  80),
    "blue":   ( 55, 115, 220),
    "yellow": (230, 205,  40),
    "purple": (160,  75, 225),
    "cyan":   ( 50, 205, 220),
    "tan":    (200, 170, 115),
    "gray":   (140, 140, 150),
    "orange": (230, 125,  35),
    "black":  ( 60,  60,  70),   # slightly blue-tinted so it reads on dark bg
}

def get_color(name: str) -> tuple[int,int,int]:
    return BALL_COLORS.get(name, (150, 150, 150))

# ── Layout constants ──────────────────────────────────────────────────────────
STACK_VISIBLE  = 7    # boxes shown per stack
BOX_SIZE       = 34   # square box side length (px)
STACK_GAP      = 5    # gap between stacks
BALL_RADIUS_FR = 0.38 # ball radius as fraction of middle-row cell width
MIDDLE_H       = 80   # height of middle row band
BOARD_PAD      = 12


class Renderer:
    def __init__(self, screen: pygame.Surface, state: GameState):
        self.screen = screen
        self.state = state
        self.font_sm = pygame.font.SysFont("monospace", 13)
        self.font_md = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_lg = pygame.font.SysFont("monospace", 48, bold=True)
        self._compute_layout()

    def _compute_layout(self):
        s = self.state
        W, H = self.screen.get_size()

        self.n_cols = len(s.stacks)
        stacks_total_w = self.n_cols * BOX_SIZE + (self.n_cols - 1) * STACK_GAP
        self.stacks_left = (W - stacks_total_w) // 2

        self.stack_section_h = (STACK_VISIBLE + 1) * BOX_SIZE + 20
        self.stack_top = 10

        self.middle_top = self.stack_top + self.stack_section_h
        self.middle_space_w = W // s.middle_spaces

        self.board_top = self.middle_top + MIDDLE_H + 8
        board_h = H - self.board_top - 10
        board_w = W - 2 * BOARD_PAD
        rows, cols = s.board_rows, s.board_cols
        self.cell_size = min(board_w // cols, board_h // rows, 64)
        total_bw = cols * self.cell_size
        total_bh = rows * self.cell_size
        self.board_left = (W - total_bw) // 2
        self.board_mid_top = self.board_top + (board_h - total_bh) // 2

    def draw(self, hovered_cell: tuple[int,int] | None = None):
        self.screen.fill(BG_COLOR)
        self._draw_stacks()
        self._draw_middle_row()
        self._draw_board(hovered_cell)
        self._draw_seed()
        self._draw_status()
        pygame.display.flip()

    # ── Stacks ────────────────────────────────────────────────────────────────

    def _draw_stacks(self):
        s = self.state
        section_bottom = self.stack_top + self.stack_section_h - 10

        for ci, stack in enumerate(s.stacks):
            # absorb_progress is owned by the stack itself now (1 - bottom_remaining)
            p = stack.absorb_progress
            bx = self.stacks_left + ci * (BOX_SIZE + STACK_GAP)
            visible = stack.colors[:STACK_VISIBLE + 1]

            for vi, color in enumerate(visible):
                if vi == 0:
                    bh = max(2, int(BOX_SIZE * (1.0 - p)))
                    by = section_bottom - bh
                else:
                    bh = BOX_SIZE
                    bottom_edge = section_bottom - int((vi - p) * BOX_SIZE)
                    by = bottom_edge - bh

                by_clipped = max(self.stack_top, by)
                bh_clipped = min(bh, by + bh - by_clipped)
                if bh_clipped <= 0:
                    continue

                rect = pygame.Rect(bx, by_clipped, BOX_SIZE, bh_clipped)
                col = get_color(color)
                pygame.draw.rect(self.screen, col, rect, border_radius=3)
                pygame.draw.rect(self.screen, _darken(col, 0.6), rect, 1, border_radius=3)

            label = self.font_sm.render(str(len(stack)), True, GRID_COLOR)
            lx = bx + BOX_SIZE // 2 - label.get_width() // 2
            self.screen.blit(label, (lx, self.stack_top))

    # ── Middle row ────────────────────────────────────────────────────────────

    def _draw_middle_row(self):
        s = self.state
        W = self.screen.get_width()
        my = self.middle_top
        mh = MIDDLE_H

        pygame.draw.rect(self.screen, MIDDLE_BG, (0, my, W, mh))

        space_w = self.middle_space_w
        r = int(space_w * BALL_RADIUS_FR * 0.9)
        cy = my + mh // 2

        for i, ball in enumerate(s.middle_row):
            cx = i * space_w + space_w // 2

            # Empty slot ring
            pygame.draw.circle(self.screen, GRID_COLOR, (cx, cy), r + 2, 1)

            if ball is None:
                continue

            col = get_color(ball.color)
            dim = _darken(col, 0.25)   # very dim tint for the empty portion

            # Background: dim tinted circle (the "empty" part)
            pygame.draw.circle(self.screen, dim, (cx, cy), r)

            # Fill from bottom: clip a rect that covers fill_fraction of the diameter
            fill_h = int(r * 2 * ball.fill_fraction)
            if fill_h > 0:
                fill_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(fill_surf, col, (r, r), r)
                # Only keep the bottom fill_h pixels
                mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                mask.fill((0, 0, 0, 0))
                pygame.draw.rect(mask, (255, 255, 255, 255),
                                 (0, r * 2 - fill_h, r * 2, fill_h))
                fill_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                self.screen.blit(fill_surf, (cx - r, cy - r))

            # Outline ring
            pygame.draw.circle(self.screen, _darken(col, 0.7), (cx, cy), r, 2)

            # Color label
            lbl = self.font_sm.render(ball.color[:3].upper(), True, TEXT_COLOR)
            self.screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    # ── Board ─────────────────────────────────────────────────────────────────

    def _draw_board(self, hovered: tuple[int,int] | None):
        s = self.state
        cs = self.cell_size
        r = int(cs * BALL_RADIUS_FR)

        for row in range(s.board_rows):
            for col in range(s.board_cols):
                cell = s.board[row][col]
                cx = self.board_left + col * cs + cs // 2
                cy = self.board_mid_top + row * cs + cs // 2
                rect = pygame.Rect(self.board_left + col * cs + 2,
                                   self.board_mid_top + row * cs + 2,
                                   cs - 4, cs - 4)

                if cell is None:
                    pygame.draw.rect(self.screen, BLOCKED_COLOR, rect, border_radius=6)
                    continue

                if cell.empty:
                    pygame.draw.rect(self.screen, EMPTY_COLOR, rect, border_radius=6)
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1, border_radius=6)
                    continue

                if not cell.unlocked:
                    pygame.draw.rect(self.screen, LOCKED_COLOR, rect, border_radius=6)
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1, border_radius=6)
                    lbl = self.font_sm.render("🔒", True, GRID_COLOR)
                    self.screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))
                    continue

                is_hovered = (hovered == (row, col))
                bg = _lighten(LOCKED_COLOR, 0.3) if is_hovered else LOCKED_COLOR
                pygame.draw.rect(self.screen, bg, rect, border_radius=6)

                ball_col = HIDDEN_COLOR if cell.hidden else get_color(cell.color)
                draw_r = r + 2 if is_hovered else r
                pygame.draw.circle(self.screen, ball_col, (cx, cy), draw_r)
                pygame.draw.circle(self.screen, _darken(ball_col, 0.6), (cx, cy), draw_r, 2)

                if cs >= 36:   # only draw label when cells are large enough to read
                    inner = "?" if cell.hidden else cell.color[:3].upper()
                    lbl = self.font_sm.render(inner, True, _darken(ball_col, 0.5) if not cell.hidden else TEXT_COLOR)
                    self.screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    # ── Seed / level ID ───────────────────────────────────────────────────────

    def _draw_seed(self):
        if self.state.seed is None:
            return
        W, H = self.screen.get_size()
        lbl = self.font_sm.render(f"ID {self.state.seed}", True, GRID_COLOR)
        self.screen.blit(lbl, (W - lbl.get_width() - 6, H - lbl.get_height() - 4))

    # ── Status overlay ────────────────────────────────────────────────────────

    def _draw_status(self):
        s = self.state
        if s.status == GameStatus.PLAYING:
            return
        W, H = self.screen.get_size()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        msg, col = ("YOU WIN!", (80, 240, 120)) if s.status == GameStatus.WON else ("DEADLOCK", (240, 80, 80))
        txt = self.font_lg.render(msg, True, col)
        self.screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - txt.get_height()//2))
        hint = self.font_md.render("Press R to restart", True, TEXT_COLOR)
        self.screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 50))

    # ── Hit testing ───────────────────────────────────────────────────────────

    def cell_at(self, mx: int, my: int) -> tuple[int,int] | None:
        s = self.state
        cs = self.cell_size
        col = (mx - self.board_left) // cs
        row = (my - self.board_mid_top) // cs
        if 0 <= row < s.board_rows and 0 <= col < s.board_cols:
            return (row, col)
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _darken(color: tuple, factor: float) -> tuple:
    return tuple(max(0, int(c * factor)) for c in color)

def _lighten(color: tuple, factor: float) -> tuple:
    return tuple(min(255, int(c + (255 - c) * factor)) for c in color)
