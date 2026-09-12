#!/usr/bin/env bash
# Dong bo tat ca .xtc trong ~/ebooks vao thu muc book/ tren MOI the SD dang cam.
# Chay: bash tools/sync-comics.sh
set -e
SRC="$HOME/ebooks"
found=0
for vol in /Volumes/*; do
  name=$(basename "$vol")
  [ "$name" = "Macintosh HD" ] && continue
  [ -d "$vol" ] || continue
  # chi coi la the X4 neu co thu muc book/ hoac cho phep tao
  dest="$vol/book"
  mkdir -p "$dest" 2>/dev/null || { echo "  bo qua $name (chi doc)"; continue; }
  echo "== The: $name -> $dest"
  for f in "$SRC"/*.xtc; do
    [ -e "$f" ] || continue
    cp -f "$f" "$dest/"
    echo "   + $(basename "$f")"
  done
  found=1
done
[ "$found" = 0 ] && echo "Khong thay the SD nao (chi co Macintosh HD). Cam the roi chay lai."
echo "Xong."
