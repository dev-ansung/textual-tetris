"""
Textual Tetris Game - Game Logic

This module contains the core game logic for the Textual Tetris Game.
It follows functional programming principles with immutable data structures.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, Mapping


# Type definitions
class TetrominoType(Enum):
    """Types of Tetromino pieces."""
    I = auto()  # I-piece (long bar)
    J = auto()  # J-piece
    L = auto()  # L-piece
    O = auto()  # O-piece (square)
    S = auto()  # S-piece
    T = auto()  # T-piece
    Z = auto()  # Z-piece


class CellState(Enum):
    """Possible states for a cell on the board."""
    EMPTY = auto()
    FILLED = auto()
    GHOST = auto()  # For ghost piece


class Direction(Enum):
    """Movement directions."""
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()


class Rotation(Enum):
    """Rotation directions."""
    CLOCKWISE = auto()
    COUNTERCLOCKWISE = auto()


@dataclass(frozen=True)
class Position:
    """Represents a position on the board."""
    row: int
    col: int
    
    def move(self, direction: Direction) -> 'Position':
        """Return a new position after moving in the given direction."""
        match direction:
            case Direction.LEFT:
                return Position(self.row, self.col - 1)
            case Direction.RIGHT:
                return Position(self.row, self.col + 1)
            case Direction.DOWN:
                return Position(self.row + 1, self.col)
            case _:
                return self


# Tetromino shape definitions
# Each shape is defined as a list of relative positions for each rotation state (0, 90, 180, 270 degrees)
# The positions are (row_offset, col_offset) from the tetromino's position
TETROMINO_SHAPES: dict[TetrominoType, list[list[tuple[int, int]]]] = {
    TetrominoType.I: [
        [(0, 0), (0, -1), (0, 1), (0, 2)],   # 0 degrees
        [(0, 0), (-1, 0), (1, 0), (2, 0)],   # 90 degrees
        [(0, 0), (0, -1), (0, 1), (0, 2)],   # 180 degrees
        [(0, 0), (-1, 0), (1, 0), (2, 0)]    # 270 degrees
    ],
    TetrominoType.J: [
        [(0, 0), (0, -1), (0, 1), (-1, 1)],  # 0 degrees
        [(0, 0), (-1, 0), (1, 0), (1, -1)],  # 90 degrees
        [(0, 0), (0, -1), (0, 1), (1, -1)],  # 180 degrees
        [(0, 0), (-1, 0), (1, 0), (-1, 1)]   # 270 degrees
    ],
    TetrominoType.L: [
        [(0, 0), (0, -1), (0, 1), (-1, -1)], # 0 degrees
        [(0, 0), (-1, 0), (1, 0), (-1, -1)], # 90 degrees
        [(0, 0), (0, -1), (0, 1), (1, 1)],   # 180 degrees
        [(0, 0), (-1, 0), (1, 0), (1, 1)]    # 270 degrees
    ],
    TetrominoType.O: [
        [(0, 0), (0, 1), (-1, 0), (-1, 1)],  # 0 degrees
        [(0, 0), (0, 1), (-1, 0), (-1, 1)],  # 90 degrees
        [(0, 0), (0, 1), (-1, 0), (-1, 1)],  # 180 degrees
        [(0, 0), (0, 1), (-1, 0), (-1, 1)]   # 270 degrees
    ],
    TetrominoType.S: [
        [(0, 0), (0, -1), (-1, 0), (-1, 1)], # 0 degrees
        [(0, 0), (-1, -1), (0, -1), (1, 0)], # 90 degrees
        [(0, 0), (0, -1), (-1, 0), (-1, 1)], # 180 degrees
        [(0, 0), (-1, -1), (0, -1), (1, 0)]  # 270 degrees
    ],
    TetrominoType.T: [
        [(0, 0), (0, -1), (0, 1), (-1, 0)],  # 0 degrees
        [(0, 0), (-1, 0), (1, 0), (0, -1)],  # 90 degrees
        [(0, 0), (0, -1), (0, 1), (1, 0)],   # 180 degrees
        [(0, 0), (-1, 0), (1, 0), (0, 1)]    # 270 degrees
    ],
    TetrominoType.Z: [
        [(0, 0), (0, 1), (-1, -1), (-1, 0)], # 0 degrees
        [(0, 0), (1, 0), (0, 1), (-1, 1)],   # 90 degrees
        [(0, 0), (0, 1), (-1, -1), (-1, 0)], # 180 degrees
        [(0, 0), (1, 0), (0, 1), (-1, 1)],   # 270 degrees
    ]
}


@dataclass(frozen=True)
class Tetromino:
    """Represents a tetromino piece."""
    type: TetrominoType
    position: Position
    rotation: int = 0  # 0, 1, 2, or 3 (0, 90, 180, 270 degrees)
    
    def rotate(self, rotation: Rotation) -> 'Tetromino':
        """Return a new tetromino after rotation."""
        new_rotation = (self.rotation + (1 if rotation == Rotation.CLOCKWISE else -1)) % 4
        return Tetromino(self.type, self.position, new_rotation)
    
    def move(self, direction: Direction) -> 'Tetromino':
        """Return a new tetromino after moving in the given direction."""
        return Tetromino(self.type, self.position.move(direction), self.rotation)
    
    def get_cells(self) -> list[Position]:
        """Get the positions of all cells occupied by this tetromino."""
        shape = TETROMINO_SHAPES[self.type][self.rotation]
        return [
            Position(self.position.row + row_offset, self.position.col + col_offset)
            for row_offset, col_offset in shape
        ]


@dataclass(frozen=True)
class Board:
    """Represents the game board."""
    width: int
    height: int
    cells: dict[tuple[int, int], TetrominoType]  # (row, col) -> tetromino type
    
    @classmethod
    def create_empty(cls, width: int = 10, height: int = 20) -> 'Board':
        """Create an empty board with the given dimensions."""
        return cls(width, height, {})
    
    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is valid (within bounds and not occupied)."""
        return (
            0 <= position.row < self.height and
            0 <= position.col < self.width and
            (position.row, position.col) not in self.cells
        )
    
    def is_valid_tetromino(self, tetromino: Tetromino) -> bool:
        """Check if a tetromino is in a valid position."""
        return all(self.is_valid_position(cell) for cell in tetromino.get_cells())
    
    def place_tetromino(self, tetromino: Tetromino) -> 'Board':
        """Return a new board with the tetromino placed."""
        new_cells = dict(self.cells)
        for cell in tetromino.get_cells():
            new_cells[(cell.row, cell.col)] = tetromino.type
        return Board(self.width, self.height, new_cells)
    
    def clear_lines(self) -> tuple['Board', int]:
        """Clear completed lines and return the new board and number of lines cleared."""
        # Find completed lines
        completed_lines = []
        for row in range(self.height):
            if all((row, col) in self.cells for col in range(self.width)):
                completed_lines.append(row)
        
        if not completed_lines:
            return self, 0
        
        # Create new cells dictionary with lines removed and cells shifted
        new_cells = {}
        
        # For each cell in the original board
        for (row, col), tetromino_type in self.cells.items():
            # Skip cells in completed lines
            if row in completed_lines:
                continue
            
            # Count how many spaces the row needs to move down
            # This is the number of completed lines
            spaces_down = len([line for line in completed_lines if line > row])
            
            new_row = row + spaces_down
            new_cells[(new_row, col)] = tetromino_type
        
        return Board(self.width, self.height, new_cells), len(completed_lines)


@dataclass(frozen=True)
class GameState:
    """Represents the current state of the game."""
    board: Board
    current_piece: Tetromino | None
    next_piece: Tetromino | None
    held_piece: TetrominoType | None
    score: int
    level: int
    lines_cleared: int
    game_over: bool
    
    @classmethod
    def new_game(cls, board_width: int = 10, board_height: int = 20) -> 'GameState':
        """Create a new game state."""
        return cls(
            board=Board.create_empty(board_width, board_height),
            current_piece=None,
            next_piece=None,
            held_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            game_over=False
        )


# Game engine functions
def create_tetromino(type: TetrominoType, position: Position) -> Tetromino:
    """Create a new tetromino of the given type at the given position."""
    return Tetromino(type, position)


def check_game_over(board: Board, next_piece_type: TetrominoType) -> bool:
    """Check if the game is over by trying to place a new piece at the starting position."""
    # For O tetromino, adjust the starting position to account for its shape
    if next_piece_type == TetrominoType.O:
        # O tetromino extends up and left from its position
        # Check if any of the 4 cells needed for the O tetromino are occupied
        if (0, 0) in board.cells or (0, 1) in board.cells or (1, 0) in board.cells or (1, 1) in board.cells:
            return True
        return False
    else:
        # Other tetrominos start at the top center
        start_position = Position(1, board.width // 2)
        new_piece = Tetromino(next_piece_type, start_position)
        
        # If the new piece can't be placed, the game is over
        return not board.is_valid_tetromino(new_piece)


def generate_next_piece(board: Board) -> Tetromino:
    """Generate a new random tetromino at the top of the board."""
    import random
    
    # Choose a random tetromino type
    tetromino_type = random.choice(list(TetrominoType))
    
    # For O tetromino, adjust the starting position to account for its shape
    if tetromino_type == TetrominoType.O:
        # O tetromino extends up and left from its position
        start_position = Position(1, board.width // 2 - 1)
    else:
        # Other tetrominos start at the top center
        start_position = Position(0, board.width // 2)
    
    return Tetromino(tetromino_type, start_position)


def update_game(state: GameState) -> GameState:
    """Update the game state for one frame."""
    if state.game_over:
        return state
    
    # If there's no current piece, spawn a new one
    if state.current_piece is None:
        # If there's no next piece, generate one
        if state.next_piece is None:
            next_piece = generate_next_piece(state.board)
            return GameState(
                board=state.board,
                current_piece=next_piece,
                next_piece=generate_next_piece(state.board),
                held_piece=state.held_piece,
                score=state.score,
                level=state.level,
                lines_cleared=state.lines_cleared,
                game_over=state.game_over
            )
        
        # Use the next piece as the current piece
        return GameState(
            board=state.board,
            current_piece=state.next_piece,
            next_piece=generate_next_piece(state.board),
            held_piece=state.held_piece,
            score=state.score,
            level=state.level,
            lines_cleared=state.lines_cleared,
            game_over=state.game_over
        )
    
    # Move the current piece down
    return move_tetromino(state, Direction.DOWN)


def move_tetromino(state: GameState, direction: Direction) -> GameState:
    """Move the current tetromino in the given direction if possible."""
    if state.current_piece is None:
        return state
    
    new_piece = state.current_piece.move(direction)
    if state.board.is_valid_tetromino(new_piece):
        return GameState(
            board=state.board,
            current_piece=new_piece,
            next_piece=state.next_piece,
            held_piece=state.held_piece,
            score=state.score,
            level=state.level,
            lines_cleared=state.lines_cleared,
            game_over=state.game_over
        )
    
    # If moving down and invalid, place the piece
    if direction == Direction.DOWN:
        new_board = state.board.place_tetromino(state.current_piece)
        new_board, lines_cleared = new_board.clear_lines()
        
        # Update score, level, etc.
        new_score = state.score + calculate_score(lines_cleared, state.level)
        new_lines_cleared = state.lines_cleared + lines_cleared
        new_level = calculate_level(new_lines_cleared)
        
        # Check for game over if we need to spawn a new piece
        game_over = False
        if state.next_piece is not None:
            game_over = check_game_over(new_board, state.next_piece.type)
        
        return GameState(
            board=new_board,
            current_piece=None,  # Will be replaced with next piece
            next_piece=state.next_piece,
            held_piece=state.held_piece,
            score=new_score,
            level=new_level,
            lines_cleared=new_lines_cleared,
            game_over=game_over
        )
    
    return state


def rotate_tetromino(state: GameState, rotation: Rotation) -> GameState:
    """Rotate the current tetromino if possible."""
    if state.current_piece is None:
        return state
    
    new_piece = state.current_piece.rotate(rotation)
    if state.board.is_valid_tetromino(new_piece):
        return GameState(
            board=state.board,
            current_piece=new_piece,
            next_piece=state.next_piece,
            held_piece=state.held_piece,
            score=state.score,
            level=state.level,
            lines_cleared=state.lines_cleared,
            game_over=state.game_over
        )
    
    return state


def hard_drop(state: GameState) -> GameState:
    """Drop the current tetromino to the bottom."""
    if state.current_piece is None:
        return state
    
    # Keep moving down until invalid
    current_state = state
    while True:
        new_state = move_tetromino(current_state, Direction.DOWN)
        if new_state.current_piece == current_state.current_piece:
            break
        current_state = new_state
    
    return current_state

def calculate_score(lines_cleared: int, level: int) -> int:
    """Calculate the score for clearing lines."""
    # Standard Tetris scoring
    match lines_cleared:
        case 1:
            return 100 * level
        case 2:
            return 300 * level
        case 3:
            return 500 * level
        case 4:
            return 800 * level
        case _:
            return 0


def calculate_level(lines_cleared: int) -> int:
    """Calculate the level based on lines cleared."""
    return (lines_cleared // 10) + 1
