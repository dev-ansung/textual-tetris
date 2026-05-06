"""
Tests for the Textual Tetris Game logic.

This module contains tests for the core game logic.
"""

import pytest

from textual_tetris_game.game import (
    Board, Direction, GameState, Position, Rotation, Tetromino, TetrominoType,
    TETROMINO_SHAPES, calculate_level, calculate_score, check_game_over, create_tetromino, 
    generate_next_piece, hard_drop,  move_tetromino, rotate_tetromino, update_game
)


def test_position_move():
    """Test the Position.move method."""
    pos = Position(1, 1)
    
    # Test moving left
    left_pos = pos.move(Direction.LEFT)
    assert left_pos.row == 1
    assert left_pos.col == 0
    
    # Test moving right
    right_pos = pos.move(Direction.RIGHT)
    assert right_pos.row == 1
    assert right_pos.col == 2
    
    # Test moving down
    down_pos = pos.move(Direction.DOWN)
    assert down_pos.row == 2
    assert down_pos.col == 1


def test_tetromino_rotate():
    """Test the Tetromino.rotate method."""
    pos = Position(1, 1)
    tetromino = Tetromino(TetrominoType.I, pos)
    
    # Test clockwise rotation
    rotated = tetromino.rotate(Rotation.CLOCKWISE)
    assert rotated.type == TetrominoType.I
    assert rotated.position == pos
    assert rotated.rotation == 1
    
    # Test multiple rotations
    rotated = rotated.rotate(Rotation.CLOCKWISE)
    assert rotated.rotation == 2
    
    rotated = rotated.rotate(Rotation.CLOCKWISE)
    assert rotated.rotation == 3
    
    rotated = rotated.rotate(Rotation.CLOCKWISE)
    assert rotated.rotation == 0
    
    # Test counter-clockwise rotation
    rotated = tetromino.rotate(Rotation.COUNTERCLOCKWISE)
    assert rotated.rotation == 3


def test_tetromino_move():
    """Test the Tetromino.move method."""
    pos = Position(1, 1)
    tetromino = Tetromino(TetrominoType.I, pos)
    
    # Test moving left
    moved = tetromino.move(Direction.LEFT)
    assert moved.type == TetrominoType.I
    assert moved.position.row == 1
    assert moved.position.col == 0
    assert moved.rotation == 0
    
    # Test moving right
    moved = tetromino.move(Direction.RIGHT)
    assert moved.position.row == 1
    assert moved.position.col == 2
    
    # Test moving down
    moved = tetromino.move(Direction.DOWN)
    assert moved.position.row == 2
    assert moved.position.col == 1


def test_board_create_empty():
    """Test the Board.create_empty method."""
    board = Board.create_empty()
    assert board.width == 10
    assert board.height == 20
    assert len(board.cells) == 0
    
    # Test with custom dimensions
    board = Board.create_empty(12, 24)
    assert board.width == 12
    assert board.height == 24


def test_board_is_valid_position():
    """Test the Board.is_valid_position method."""
    board = Board.create_empty(10, 20)
    
    # Test valid positions
    assert board.is_valid_position(Position(0, 0))
    assert board.is_valid_position(Position(19, 9))
    
    # Test invalid positions (out of bounds)
    assert not board.is_valid_position(Position(-1, 0))
    assert not board.is_valid_position(Position(0, -1))
    assert not board.is_valid_position(Position(20, 0))
    assert not board.is_valid_position(Position(0, 10))
    
    # Test with occupied cells
    board_with_cells = Board(10, 20, {(1, 1): TetrominoType.I})
    assert not board_with_cells.is_valid_position(Position(1, 1))


def test_calculate_score():
    """Test the calculate_score function."""
    # Test scoring for different line clears
    assert calculate_score(0, 1) == 0
    assert calculate_score(1, 1) == 100
    assert calculate_score(2, 1) == 300
    assert calculate_score(3, 1) == 500
    assert calculate_score(4, 1) == 800
    
    # Test level multiplier
    assert calculate_score(1, 2) == 200
    assert calculate_score(2, 3) == 900
    assert calculate_score(4, 5) == 4000


def test_calculate_level():
    """Test the calculate_level function."""
    assert calculate_level(0) == 1
    assert calculate_level(9) == 1
    assert calculate_level(10) == 2
    assert calculate_level(19) == 2
    assert calculate_level(20) == 3
    assert calculate_level(99) == 10
    assert calculate_level(100) == 11


def test_tetromino_get_cells():
    """Test the Tetromino.get_cells method."""
    # Test I-piece at rotation 0
    tetromino = Tetromino(TetrominoType.I, Position(5, 5), 0)
    cells = tetromino.get_cells()
    assert len(cells) == 4
    assert Position(5, 5) in cells  # Center
    assert Position(5, 4) in cells  # Left
    assert Position(5, 6) in cells  # Right
    assert Position(5, 7) in cells  # Far right
    
    # Test I-piece at rotation 1 (90 degrees)
    tetromino = Tetromino(TetrominoType.I, Position(5, 5), 1)
    cells = tetromino.get_cells()
    assert len(cells) == 4
    assert Position(5, 5) in cells  # Center
    assert Position(4, 5) in cells  # Up
    assert Position(6, 5) in cells  # Down
    assert Position(7, 5) in cells  # Far down
    
    # Test O-piece (should be the same at all rotations)
    tetromino = Tetromino(TetrominoType.O, Position(5, 5), 0)
    cells = tetromino.get_cells()
    assert len(cells) == 4
    assert Position(5, 5) in cells  # Bottom right
    assert Position(5, 6) in cells  # Bottom left
    assert Position(4, 5) in cells  # Top right
    assert Position(4, 6) in cells  # Top left


def test_board_clear_lines():
    """Test the Board.clear_lines method."""
    # Create a board with some cells
    cells = {}
    
    # Add a complete line at row 18
    for col in range(10):
        cells[(18, col)] = TetrominoType.I
    
    # Add some cells in row 17
    cells[(17, 0)] = TetrominoType.J
    cells[(17, 1)] = TetrominoType.J
    
    # Add a complete line at row 16
    for col in range(10):
        cells[(16, col)] = TetrominoType.T
    
    board = Board(10, 20, cells)
    
    # Clear lines
    new_board, lines_cleared = board.clear_lines()
    
    # Check results
    assert lines_cleared == 2  # Two complete lines
    assert len(new_board.cells) == 2  # Only the two cells from row 17 remain
    
    # Check that the cells from row 17 have been moved down
    # Since we're counting lines below the row, and both completed lines (16 and 18)
    # are below row 17, the cells should be moved down by 2 to row 19
    assert (18, 0) in new_board.cells
    assert (18, 1) in new_board.cells
    assert new_board.cells[(18, 0)] == TetrominoType.J
    assert new_board.cells[(18, 1)] == TetrominoType.J


def test_check_game_over():
    """Test the check_game_over function."""
    # Create an empty board
    board = Board.create_empty()
    
    # Game should not be over on an empty board
    assert not check_game_over(board, TetrominoType.I)
    
    # Create a board with cells at the top center
    cells = {}
    for col in range(4, 7):  # Block the center of the top row
        cells[(1, col)] = TetrominoType.I
    
    board_with_top_center_cells = Board(10, 20, cells)
    
    # Game should be over if a piece can't be placed at the top center
    assert check_game_over(board_with_top_center_cells, TetrominoType.I)
    
    # Create a board with cells at the top left (where O tetromino spawns)
    cells_left = {}
    # Block the top-left corner where O tetromino spawns
    cells_left[(0, 0)] = TetrominoType.I
    cells_left[(0, 1)] = TetrominoType.I
    cells_left[(1, 0)] = TetrominoType.I
    cells_left[(1, 1)] = TetrominoType.I
    
    board_with_top_left_cells = Board(10, 20, cells_left)
    
    # Game should be over for O tetromino if its spawn area is blocked
    assert check_game_over(board_with_top_left_cells, TetrominoType.O)
    
    # But O tetromino should fit if center is blocked but left is clear
    assert not check_game_over(board_with_top_center_cells, TetrominoType.O)


def test_game_state_new_game():
    """Test the GameState.new_game method."""
    state = GameState.new_game()
    assert state.board.width == 10
    assert state.board.height == 20
    assert state.current_piece is None
    assert state.next_piece is None
    assert state.held_piece is None
    assert state.score == 0
    assert state.level == 1
    assert state.lines_cleared == 0
    assert not state.game_over
    
    # Test with custom dimensions
    state = GameState.new_game(12, 24)
    assert state.board.width == 12
    assert state.board.height == 24
