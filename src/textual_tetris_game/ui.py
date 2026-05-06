"""
Textual Tetris Game - User Interface

This module contains the Textual UI components for the Tetris game.
It uses the Textual framework to create a rich terminal user interface.
"""

import asyncio

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Center
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static
from textual.worker import Worker, WorkerState

from textual_tetris_game.game import (
    Board, Direction, GameState, Rotation, TetrominoType,
    TETROMINO_SHAPES, hard_drop,  move_tetromino, 
    rotate_tetromino, update_game
)


class BoardWidget(Static):
    """Widget that displays the Tetris game board."""
    
    DEFAULT_CSS = """
    BoardWidget {
        width: 24;
        height: 24;
        border: solid $primary;
        content-align: center middle;
    }
    """
    
    board_state: reactive[Board | None] = reactive(None)
    current_piece: reactive[any | None] = reactive(None)
    
    def render(self) -> str:
        """Render the game board."""
        if self.board_state is None:
            return "Loading..."
        
        # Create a 2D grid representation of the board
        grid = [["  " for _ in range(self.board_state.width)] for _ in range(self.board_state.height)]
        
        # Fill in the cells from the board state
        for (row, col), tetromino_type in self.board_state.cells.items():
            if 0 <= row < self.board_state.height and 0 <= col < self.board_state.width:
                grid[row][col] = f"[on green]  [/on green]"
        
        # Add the current piece to the grid
        if self.current_piece is not None:
            for cell in self.current_piece.get_cells():
                if 0 <= cell.row < self.board_state.height and 0 <= cell.col < self.board_state.width:
                    grid[cell.row][cell.col] = f"[on green]  [/on green]"
        
        # Construct the board string with borders
        board_str = "┌" + "─" * (self.board_state.width * 2) + "┐\n"
        
        for row in grid:
            board_str += "│" + "".join(cell for cell in row) + "│\n"
        
        board_str += "└" + "─" * (self.board_state.width * 2) + "┘"
        
        return board_str


class NextPieceWidget(Static):
    """Widget that displays the next piece."""
    
    DEFAULT_CSS = """
    NextPieceWidget {
        width: 10;
        height: 6;
        border: solid $primary;
        content-align: center middle;
    }
    """
    
    next_piece = reactive(None)

    def render(self) -> str:
        """Render the next piece."""
        if self.next_piece is None:
            return "Next:\n\nNone"
        
        # Create a small grid to display the next piece
        grid = [["  " for _ in range(4)] for _ in range(2)]
        
        # Get the shape of the next piece at rotation 0
        tetromino_type = self.next_piece.type
        shape = TETROMINO_SHAPES[tetromino_type][0]
        
        # Calculate the center position for the preview
        center_row, center_col = 1, 1
        if tetromino_type == TetrominoType.O:
            center_row, center_col = 1, 1
        
        # Add the piece to the grid
        for row_offset, col_offset in shape:
            row = center_row + row_offset
            col = center_col + col_offset
            if 0 <= row < 2 and 0 <= col < 4:
                grid[row][col] = f"[on green]  [/on green]"
        
        # Construct the preview string
        preview_str = "Next:\n\n"
        for row in grid:
            preview_str += "".join(cell for cell in row) + "\n"
        
        return preview_str

class ScoreWidget(Static):
    """Widget that displays the score and level."""
    
    DEFAULT_CSS = """
    ScoreWidget {
        width: 10;
        height: 8;
        border: solid $primary;
        content-align: center middle;
    }
    """
    score: reactive[int] = reactive(0)
    level: reactive[int] = reactive(1)
    lines_cleared: reactive[int] = reactive(0)
    
    def render(self) -> str:
        """Render the score and level."""
        return f"Score: {self.score}\n\nLevel: {self.level}\n\nLines: {self.lines_cleared}"


class ControlsWidget(Static):
    """Widget that displays the game controls."""
    
    DEFAULT_CSS = """
    ControlsWidget {
        width: 10;
        height: 10;
        border: solid $primary;
        content-align: center middle;
    }
    """
    
    def render(self) -> str:
        """Render the controls."""
        return (
            "Controls:\n\n"
            "←/→: Move\n"
            "↓: Soft Drop\n"
            "↑: Rotate\n"
            "Space: Hard Drop\n"
            "P: Pause"
        )


class PauseOverlay(Static):
    """Overlay that displays when the game is paused."""
    
    DEFAULT_CSS = """
    PauseOverlay {
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        color: $text;
        content-align: center middle;
        layer: overlay;
    }
    """
    
    def render(self) -> str:
        """Render the pause overlay."""
        return "[bold]PAUSED[/bold]\n\nPress P to resume"


class GameScreen(Screen):
    """The main game screen."""
    CSS = """
    /* Remove extra space around the container */
    Horizontal {
        padding: 0;
        margin: 0;
        width: 50;
    }
    """

    BINDINGS = [
        Binding("left", "move_left", "Move Left"),
        Binding("right", "move_right", "Move Right"),
        Binding("down", "soft_drop", "Soft Drop"),
        Binding("up", "rotate", "Rotate"),
        Binding("space", "hard_drop", "Hard Drop"),
        Binding("p", "toggle_pause", "Pause/Resume"),
    ]
    game_state: reactive[GameState] = reactive(GameState.new_game())
    paused: reactive[bool] = reactive(False)
    
    def watch_paused(self, paused: bool) -> None:
        """Watch for changes to the paused state."""
        if paused:
            self.mount(PauseOverlay())
        else:
            try:
                self.query_one(PauseOverlay).remove()
            except NoMatches:
                pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_worker: Worker | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the game screen layout."""
        with Center():
            with Horizontal():
                with Vertical():
                    yield BoardWidget()
                with Vertical():
                    yield NextPieceWidget()
                    yield ScoreWidget()
                    yield ControlsWidget()
    
    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Initialize the game state with a new piece
        self.game_state = update_game(self.game_state)
        self.update_ui()
        
        # Start the game worker to handle automatic piece movement
        self.start_game_worker()
    
    def start_game_worker(self) -> None:
        """Start the game loop in a worker."""
        if self.game_worker is None or self.game_worker.state == WorkerState.ERROR:
            self.run_worker(self.game_loop())
    
    async def game_loop(self) -> None:
        """Game loop that updates the game state."""
        while True:
            if not self.paused and not self.game_state.game_over:
                # Update game state
                self.game_state = update_game(self.game_state)
                
                # Update UI
                self.update_ui()
            
            # Control game speed based on level
            await asyncio.sleep(self.get_delay_for_level())
    
    def get_delay_for_level(self) -> float:
        """Get the delay between game updates based on the current level."""
        # Standard Tetris speed formula
        return max(0.1, 1.0 - (self.game_state.level - 1) * 0.05)
    
    def update_ui(self) -> None:
        """Update the UI with the current game state."""
        try:
            board_widget = self.query_one(BoardWidget)
            board_widget.board_state = self.game_state.board
            board_widget.current_piece = self.game_state.current_piece
            
            next_piece_widget = self.query_one(NextPieceWidget)
            next_piece_widget.next_piece = self.game_state.next_piece
            
            score_widget = self.query_one(ScoreWidget)
            score_widget.score = self.game_state.score
            score_widget.level = self.game_state.level
            score_widget.lines_cleared = self.game_state.lines_cleared
            
            # Check for game over
            if self.game_state.game_over:
                self.handle_game_over()
        except NoMatches:
            # Widgets not mounted yet
            pass
    
    def handle_game_over(self) -> None:
        """Handle game over state."""
        # Stop the game worker
        if self.game_worker is not None:
            self.game_worker.stop()
            self.game_worker = None
        
        # Show the game over screen
        self.app.show_game_over(self.game_state.score)
    
    def action_move_left(self) -> None:
        """Move the current piece left."""
        if not self.paused and not self.game_state.game_over:
            self.game_state = move_tetromino(self.game_state, Direction.LEFT)
            self.update_ui()
    
    def action_move_right(self) -> None:
        """Move the current piece right."""
        if not self.paused and not self.game_state.game_over:
            self.game_state = move_tetromino(self.game_state, Direction.RIGHT)
            self.update_ui()
    
    def action_soft_drop(self) -> None:
        """Soft drop the current piece."""
        if not self.paused and not self.game_state.game_over:
            self.game_state = move_tetromino(self.game_state, Direction.DOWN)
            self.update_ui()
    
    def action_rotate(self) -> None:
        """Rotate the current piece."""
        if not self.paused and not self.game_state.game_over:
            self.game_state = rotate_tetromino(self.game_state, Rotation.CLOCKWISE)
            self.update_ui()
    
    def action_hard_drop(self) -> None:
        """Hard drop the current piece."""
        if not self.paused and not self.game_state.game_over:
            self.game_state = hard_drop(self.game_state)
            self.update_ui()
    
    def action_toggle_pause(self) -> None:
        """Pause or resume the game."""
        self.paused = not self.paused


class StartScreen(Screen):
    """The start screen."""
    
    def compose(self) -> ComposeResult:
        """Compose the start screen layout."""
        yield Header(show_clock=True)
        with Container():
            yield Label("Textual Tetris", id="title")
            yield Label("A terminal-based Tetris game using Textual", id="subtitle")
            with Center():
                yield Button("Start Game", id="start-button", variant="primary")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-button":
            # Create a new game screen instance
            game_screen = GameScreen()
            self.app.push_screen(game_screen)


class GameOverScreen(Screen):
    """The game over screen."""
    
    def __init__(self, score: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = score
    
    def compose(self) -> ComposeResult:
        """Compose the game over screen layout."""
        yield Header(show_clock=True)
        with Container():
            yield Label("Game Over", id="title")
            with Center():
                yield Label(f"Final Score: {self.score}", id="score")
                yield Button("Play Again", id="restart-button", variant="primary")
                yield Button("Quit", id="quit-button", variant="error")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "restart-button":
            # Create a new game screen instance
            game_screen = GameScreen()
            self.app.push_screen(game_screen)
        elif event.button.id == "quit-button":
            self.app.exit()


class TetrisApp(App):
    """The main Tetris application."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #title {
        content-align: center middle;
        text-style: bold;
        width: 100%;
        height: 3;
        margin: 1 0;
    }
    
    #subtitle {
        content-align: center middle;
        width: 100%;
        height: 3;
        margin: 1 0;
    }
    
    #start-button, #restart-button, #quit-button {
        width: 16;
        margin: 1 0;
    }
    
    Container {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    Button {
        margin: 1 2;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    SCREENS = {
        "start": StartScreen,
        "game": GameScreen,
    }
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.push_screen("start")
    
    def show_game_over(self, score: int) -> None:
        """Show the game over screen with the final score."""
        self.push_screen(GameOverScreen(score))
