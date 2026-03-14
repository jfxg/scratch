"""Loads a level into GameState from a dict or a JSON file path."""
import json
from game.state import GameState, BoxStack, BoardCell


def build_state(data: dict) -> GameState:
    """Convert a level data dict into a GameState."""
    stacks = [BoxStack(list(col)) for col in data["stacks"]]
    middle_spaces = data.get("middle_spaces", 7)
    middle_row = [None] * middle_spaces

    raw_board = data["board"]["cells"]
    board = []
    for r, row in enumerate(raw_board):
        board_row = []
        for cell in row:
            if cell is None:
                board_row.append(None)
            else:
                board_row.append(BoardCell(
                    color=cell["color"],
                    hidden=cell.get("hidden", False),
                    unlocked=(r == 0),
                    empty=False,
                ))
        board.append(board_row)

    return GameState(
        stacks=stacks,
        middle_spaces=middle_spaces,
        middle_row=middle_row,
        board=board,
        seed=data.get("seed"),
    )


def load_level(path: str) -> GameState:
    with open(path) as f:
        data = json.load(f)
    return build_state(data)
