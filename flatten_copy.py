# flatten_copy.py
#!/usr/bin/env python3
"""
Flatten a file or directory by compressing each path (excluding extension) with zlib+Base64,
copying into a flat destination folder using the token as filename + original extension.
Exports a CSV mapping of token->original path, and shows a progress bar.

Usage:
  # Flatten and copy a directory tree:
  python flatten_copy.py source_dir dest_dir [-l LEVEL] [-m mapping.csv]

  # Flatten and copy a single file:
  python flatten_copy.py file.ext dest_dir [-l LEVEL] [-m mapping.csv]

  # Just show flattened name without copying:
  python flatten_copy.py file.ext
"""
import argparse, os, sys, base64, zlib, shutil, csv


def print_progress(current, total, prefix='', length=30):
    frac = current / total
    filled = int(length * frac)
    bar = '#' * filled + '-' * (length - filled)
    sys.stderr.write(f"\r{prefix} |{bar}| {current}/{total}")
    sys.stderr.flush()


def compress_name(path: str, level: int = 9) -> str:
    base, ext = os.path.splitext(path)
    data = base.encode('utf-8')
    compressed = zlib.compress(data, level)
    token = base64.urlsafe_b64encode(compressed).decode('ascii').rstrip('=')
    return f"{token}{ext}"


def flatten_file(src: str, dest_dir: str, level: int):
    mapping = []
    token_name = compress_name(os.path.basename(src), level)
    os.makedirs(dest_dir, exist_ok=True)
    dst = os.path.join(dest_dir, token_name)
    shutil.copy2(src, dst)
    print(f"Copied {src} -> {dst}")
    mapping.append((token_name, os.path.basename(src)))
    return mapping


def flatten_directory(src_dir: str, dest_dir: str, level: int):
    mapping = []
    # gather all files
    all_files = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, src_dir)
            all_files.append((full, rel))
    total = len(all_files)
    for idx, (full, rel) in enumerate(all_files, 1):
        token_name = compress_name(rel, level)
        os.makedirs(dest_dir, exist_ok=True)
        dst = os.path.join(dest_dir, token_name)
        shutil.copy2(full, dst)
        print_progress(idx, total, prefix='Flattening')
        mapping.append((token_name, rel))
    print()  # newline after progress
    return mapping


def write_mapping_csv(mapping, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(['token', 'original'])
        writer.writerows(mapping)
    print(f"Mapping exported to {csv_path}")


def main():
    p = argparse.ArgumentParser(description='Flatten and copy paths with progress and mapping CSV')
    p.add_argument('source', help='File or directory to flatten')
    p.add_argument('dest', nargs='?', help='Destination folder to copy flattened files')
    p.add_argument('-l', '--level', type=int, choices=range(0,10), default=9,
                   help='zlib compression level (0-9), default 9')
    p.add_argument('-m', '--map', dest='mapcsv', help='Path to output mapping CSV (default: dest/mapping.csv)')
    args = p.parse_args()

    if args.dest:
        if os.path.isdir(args.source):
            mapping = flatten_directory(args.source, args.dest, args.level)
        elif os.path.isfile(args.source):
            mapping = flatten_file(args.source, args.dest, args.level)
        else:
            print("Error: source not found", file=sys.stderr)
            sys.exit(1)
        # write mapping CSV
        csv_path = args.mapcsv or os.path.join(args.dest, 'mapping.csv')
        write_mapping_csv(mapping, csv_path)
    else:
        # no copying, just print the flattened name
        print(compress_name(args.source, args.level))

if __name__ == '__main__':
    main()