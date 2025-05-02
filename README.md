# Flatten & Copy

Flatten a file or directory by compressing each path (excluding extension) with zlib+Base64,
copying into a flat destination folder using the token as filename + original extension.
Exports a CSV mapping of token->original path, and shows a progress bar.

## Usage:
  ### Flatten and copy a directory tree:
  ```
  python flatten_copy.py source_dir dest_dir [-l LEVEL] [-m mapping.csv]
  ```
  ### Flatten and copy a single file:
  ```
  python flatten_copy.py file.ext dest_dir [-l LEVEL] [-m mapping.csv]
  ```
  ### Just show flattened name without copying:
  ```
  python flatten_copy.py file.ext
  ```
