# Textual Tetris

![Demo](demo.gif)

A terminal-based implementation of the classic Tetris game using the [Textual](https://textual.textualize.io/) framework.

## Features

- **Rich Terminal UI**: Built with the Textual framework for a responsive experience.
- **Visual Guides**: Includes color-coded tetrominoes and a ghost piece guide.
- **Game Mechanics**: Features classic Tetris scoring, a leveling system with increasing speed, and next piece preview.
- **Controls**: Supports standard movement, soft drop, hard drop, and rotation.
- **Modern Python**: Requires Python 3.14+ and uses `uv` for dependency management.

## Quick Start

Run the game directly with `uv`:

```bash
uvx --from git+https://github.com/dev-ansung/textual-tetris tetris
```

## Controls

| Key | Action |
|-----|--------|
| `Left` / `Right` | Move Left / Right |
| `Down` | Soft Drop |
| `Up` | Rotate Clockwise |
| `Space` | Hard Drop |
| `P` | Pause / Resume |
| `Q` | Quit |

## Installation and Development

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dev-ansung/textual-tetris.git
   cd textual-tetris
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the game:
   ```bash
   uv run tetris
   ```

### Testing

Run the test suite:
```bash
uv run test
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
