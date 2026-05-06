"""
Textual Tetris Game - Command Line Interface

This module provides the command-line interface for the Textual Tetris Game.
It handles argument parsing and launches the main application.
"""

import sys

from textual_tetris_game.ui import TetrisApp


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the Textual Tetris Game.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="tetris",
        description="A terminal-based Tetris game using the Textual framework.",
        epilog="""
Controls:
  ← / →       Move Left / Right
  ↓           Soft Drop
  ↑           Rotate Clockwise
  Space       Hard Drop
  P           Pause / Resume
  Q           Quit
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Parse arguments but we don't have any specific ones yet
    # This will handle -h/--help automatically
    parser.parse_args(argv[1:] if argv is not None else sys.argv[1:])
    
    app = TetrisApp()
    app.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
