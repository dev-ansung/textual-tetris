# Textual Tetris

A terminal-based implementation of the classic Tetris game using the [Textual](https://textual.textualize.io/) framework.


## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) - Python package and dependency manager
- [textual](https://textual.textualize.io/) - Terminal UI framework

## Quick Start

Install `textual-tetris-game` with `uv`:

```bash
uv tool install git+https://github.com/ar90n/textual-tetris-game
```

Run the game:

```bash
uv run tetris
```

Or run with `uvx` without installation:

```bash
uvx --from git+https://github.com/ar90n/textual-tetris-game tetris
```

## Usage

### CLI

```bash
usage: tetris [-h]

A terminal-based Tetris game using the Textual framework.

options:
  -h, --help  show this help message and exit

Controls:
  ← / →       Move Left / Right
  ↓           Soft Drop
  ↑           Rotate Clockwise
  Space       Hard Drop
  P           Pause / Resume
  Q           Quit
```

### Controls

| Key | Action |
|-----|--------|
| `←` / `→` | Move Left / Right |
| `↓` | Soft Drop |
| `↑` | Rotate Clockwise |
| `Space` | Hard Drop |
| `P` | Pause / Resume |
| `Q` | Quit |

### Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/ar90n/textual-tetris-game
cd textual-tetris-game
uv sync
```

Run the test suite:

```bash
uv run test
```

## License

[MIT License](LICENSE)
