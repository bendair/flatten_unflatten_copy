# unflatten_copy.py
#!/usr/bin/env python3
"""
Unflatten flat files back to their original folder-file paths under a given root.
Exports a CSV mapping of token->restored path, and shows a progress bar.

Usage:
  # Restore entire flat directory:
  python unflatten_copy.py flat_dir restore_root [-m mapping.csv]

  # Restore a single file:
  python unflatten_copy.py flat_dir/TOKEN.ext restore_root [-m mapping.csv]
"""
import argparse, os, sys, base64, zlib, shutil, csv


def print_progress(current, total, prefix='', length=30):
    frac = current / total
    filled = int(length * frac)
    bar = '#' * filled + '-' * (length - filled)
    sys.stderr.write(f"\r{prefix} |{bar}| {current}/{total}")
    sys.stderr.flush()


def decompress_name(token_file: str) -> str:
    base, ext = os.path.splitext(token_file)
    padding = '=' * (-len(base) % 4)
    compressed = base64.urlsafe_b64decode(base + padding)
    data = zlib.decompress(compressed)
    path = data.decode('utf-8')
    return path + ext


def restore_file(src: str, dest_root: str):
    token = os.path.basename(src)
    rel_path = decompress_name(token)
    dst = os.path.join(dest_root, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Restored {token} -> {dst}")
    return (token, rel_path)


def restore_directory(flat_dir: str, dest_root: str):
    mapping = []
    files = [f for f in os.listdir(flat_dir) if os.path.isfile(os.path.join(flat_dir, f))]
    total = len(files)
    for idx, token in enumerate(files, 1):
        src = os.path.join(flat_dir, token)
        rel_path = decompress_name(token)
        dst = os.path.join(dest_root, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print_progress(idx, total, prefix='Restoring')
        mapping.append((token, rel_path))
    print()
    return mapping


def write_mapping_csv(mapping, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(['token', 'restored'])
        writer.writerows(mapping)
    print(f"Mapping exported to {csv_path}")


def main():
    p = argparse.ArgumentParser(description='Restore flattened files with progress and mapping CSV')
    p.add_argument('src', help='Flat directory or single flattened file')
    p.add_argument('dest', help='Root folder to restore files into')
    p.add_argument('-m', '--map', dest='mapcsv', help='Path to output mapping CSV (default: dest/mapping.csv)')
    args = p.parse_args()

    if os.path.isdir(args.src):
        mapping = restore_directory(args.src, args.dest)
    elif os.path.isfile(args.src):
        entry = restore_file(args.src, args.dest)
        mapping = [entry]
    else:
        print("Error: source not found", file=sys.stderr)
        sys.exit(1)
    # write mapping CSV
    csv_path = args.mapcsv or os.path.join(args.dest, 'mapping.csv')
    write_mapping_csv(mapping, csv_path)

if __name__ == '__main__':
    main()