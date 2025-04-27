#!/usr/bin/env python3
"""
CodeClip - A command line utility for macOS to copy source code from directories to clipboard
for sharing with LLMs.

Usage:
    codeclip.py PATH [--extensions EXT1,EXT2,...] [--exclude DIR1,DIR2,...] 
                    [--max-size SIZE_KB] [--max-depth DEPTH]

Examples:
    codeclip.py ~/projects/myapp --extensions py,js,html --exclude node_modules,venv --max-size 100
"""

import os
import sys
import glob
import argparse
import subprocess
from datetime import datetime


def format_size(size_bytes):
    """Format file size in a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def should_include_file(file_path, extensions=None):
    """Check if file should be included based on extensions."""
    if extensions is None:
        return True
    return any(file_path.endswith('.' + ext) for ext in extensions)


def get_filtered_directory_structure(path, extensions=None, exclude_dirs=None, max_depth=None, current_depth=0):
    """Generate a string representation of directory structure, filtered by extensions."""
    if max_depth is not None and current_depth > max_depth:
        return "..."
    
    structure = []
    try:
        items = sorted(os.listdir(path))
        for item in items:
            item_path = os.path.join(path, item)
            
            # Skip excluded directories
            if os.path.isdir(item_path) and exclude_dirs and item in exclude_dirs:
                continue
                
            if os.path.isdir(item_path):
                # Check if directory contains any matching files before including it
                has_matching_files = False
                
                for root, _, files in os.walk(item_path):
                    if any(should_include_file(os.path.join(root, f), extensions) for f in files):
                        has_matching_files = True
                        break
                    
                    # Respect exclude_dirs for subdirectories
                    if exclude_dirs:
                        for exclude_dir in exclude_dirs:
                            if exclude_dir in os.path.basename(root):
                                # Skip this directory
                                continue
                
                if has_matching_files or extensions is None:
                    structure.append(f"{item}/")
                    if max_depth is None or current_depth < max_depth:
                        sub_structure = get_filtered_directory_structure(
                            item_path, extensions, exclude_dirs, max_depth, current_depth + 1
                        )
                        if sub_structure:
                            structure.append("  " + "\n  ".join(sub_structure.split("\n")))
            elif should_include_file(item_path, extensions):
                structure.append(item)
    except PermissionError:
        structure.append("(Permission denied)")
    
    return "\n".join(structure)


def process_files(directory, extensions=None, exclude_dirs=None, max_size=None, max_depth=None):
    """Process all files in the directory and return formatted content."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Convert extensions to a list if it's a string
    if isinstance(extensions, str):
        extensions = extensions.split(',')
    
    result = []
    
    # Add filtered directory structure
    result.append("# Directory Structure (Filtered)\n```")
    result.append(get_filtered_directory_structure(directory, extensions, exclude_dirs, max_depth))
    result.append("```\n")
    
    # Process files
    result.append("# Source Files\n")
    
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Check depth
        relative_path = os.path.relpath(root, directory)
        current_depth = 0 if relative_path == '.' else relative_path.count(os.sep) + 1
        if max_depth is not None and current_depth >= max_depth:
            dirs[:] = []  # Don't go deeper
            continue
        
        for file in sorted(files):
            # Filter by extension if specified
            if extensions and not any(file.endswith('.' + ext) for ext in extensions):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                # Get file stats
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                
                # Skip if file is too large
                if max_size is not None and file_size > max_size * 1024:
                    result.append(f"# SKIPPED (TOO LARGE): {os.path.relpath(file_path, directory)}")
                    result.append(f"# Size: {format_size(file_size)}")
                    result.append("")
                    continue
                
                # File metadata
                mod_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                relative_path = os.path.relpath(file_path, directory)
                
                result.append(f"## File: {relative_path}")
                result.append(f"## Size: {format_size(file_size)} | Last Modified: {mod_time}")
                result.append("```")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    result.append(content)
                
                result.append("```")
                result.append("")  # Empty line for separation
                file_count += 1
                
            except (PermissionError, UnicodeDecodeError, IsADirectoryError) as e:
                result.append(f"# ERROR reading {os.path.relpath(file_path, directory)}: {str(e)}")
                result.append("")
    
    # Add summary
    result.insert(0, f"# CodeClip Output - {file_count} files from {os.path.abspath(directory)}\n")
    
    return "\n".join(result)


def copy_to_clipboard(text):
    """Copy text to macOS clipboard."""
    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))
    return process.returncode


def main():
    parser = argparse.ArgumentParser(description="Copy source code from directories to clipboard for LLMs")
    parser.add_argument("path", help="Path to the directory containing source code")
    parser.add_argument("--extensions", "-e", help="Comma-separated list of file extensions to include")
    parser.add_argument("--exclude", "-x", help="Comma-separated list of directories to exclude")
    parser.add_argument("--max-size", "-s", type=int, default=500, 
                        help="Maximum file size in KB (default: 500KB)")
    parser.add_argument("--max-depth", "-d", type=int, help="Maximum directory depth to traverse")
    
    args = parser.parse_args()
    
    # Verify the path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)
    
    # Process extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    # Process excluded directories
    exclude_dirs = []
    if args.exclude:
        exclude_dirs = [dir.strip() for dir in args.exclude.split(',')]
    
    try:
        # Process files
        output = process_files(
            args.path, 
            extensions=extensions,
            exclude_dirs=exclude_dirs,
            max_size=args.max_size,
            max_depth=args.max_depth
        )
        
        # Copy to clipboard
        if copy_to_clipboard(output) == 0:
            print(f"Success! Copied {args.path} code to clipboard.")
            print(f"Extensions filter: {extensions or 'None'}")
            print(f"Excluded directories: {exclude_dirs or 'None'}")
            print(f"Max file size: {args.max_size}KB")
            print(f"Max depth: {args.max_depth or 'No limit'}")
        else:
            print("Error: Failed to copy to clipboard.")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
