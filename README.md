# CodeClip

A command-line utility for macOS that copies source code from directories to your clipboard in a format optimized for LLMs like Gemini, ChatGPT, Claude, and others.

## Features

- 📋 Copies source code directly to clipboard
- 🗂️ Includes filtered directory structure
- 📝 Adds file metadata (name, path, size, last modified)
- 🔍 Filters by file extension
- 🚫 Excludes specified directories
- 📏 Limits file size to avoid copying large files
- 🌳 Controls directory traversal depth

## Installation

### Option 1: Using the installation script

```bash
# Clone the repository
git clone https://github.com/yourusername/codeclip.git
cd codeclip

# Run the installation script
chmod +x install_codeclip.sh
./install_codeclip.sh
```

### Option 2: Manual installation

```bash
# Download the codeclip.py file
# Make it executable
chmod +x codeclip.py
# Move it to your PATH
sudo mv codeclip.py /usr/local/bin/codeclip
```

## Usage

```bash
codeclip /path/to/directory [options]
```

### Examples

```bash
# Copy all files from a project
codeclip ~/projects/myapp

# Filter by file extensions
codeclip ~/projects/myapp --extensions py,js,html

# Exclude certain directories
codeclip ~/projects/myapp --exclude node_modules,venv,dist

# Limit file size (in KB)
codeclip ~/projects/myapp --max-size 100

# Control how deep to traverse
codeclip ~/projects/myapp --max-depth 2

# Combine options
codeclip ~/projects/myapp --extensions py,js --exclude node_modules --max-size 200 --max-depth 3
```

### Options

| Option | Description |
|--------|-------------|
| `--extensions`, `-e` | Comma-separated list of file extensions to include |
| `--exclude`, `-x` | Comma-separated list of directories to exclude |
| `--max-size`, `-s` | Maximum file size in KB (default: 500KB) |
| `--max-depth`, `-d` | Maximum directory depth to traverse |

## Output Format

The clipboard content is formatted in Markdown, making it ideal for pasting into LLMs.


## Why use CodeClip?

- **Contextual Understanding**: Helps LLMs understand your code structure
- **Time-Saving**: No need to manually copy multiple files
- **Better Responses**: Provides LLMs with file metadata for more accurate help
- **Mac-Optimized**: Built specifically for macOS clipboard integration

## Requirements

- macOS
- Python 3.6+

## License

MIT

