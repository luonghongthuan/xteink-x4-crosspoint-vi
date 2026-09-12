#!/usr/bin/env bash
# Dong bo sach tu ~/ebooks vao thu muc book/ tren MOI the SD dang cam.
# Chep ca truyen tranh (.xtc) lan sach chu (.epub), gom ca file trong thu muc con.
# Chay: bash tools/sync-comics.sh
set -e
SRC="$HOME/ebooks"
found=0
for vol in /Volumes/*; do
  name=$(basename "$vol")
  [ "$name" = "Macintosh HD" ] && continue
  [ -d "$vol" ] || continue
  dest="$vol/book"
  mkdir -p "$dest" 2>/dev/null || { echo "  bo qua $name (chi doc)"; continue; }
  echo "== The: $name -> $dest"
  # -maxdepth 2: bat file ngay trong ~/ebooks va trong thu muc con (vd bo truyen nhieu tap)
  find "$SRC" -maxdepth 2 \( -iname "*.xtc" -o -iname "*.epub" \) -print0 2>/dev/null |
  while IFS= read -r -d '' f; do
    cp -f "$f" "$dest/"
    echo "   + $(basename "$f")"
  done
  found=1
done
[ "$found" = 0 ] && echo "Khong thay the SD nao (chi co Macintosh HD). Cam the roi chay lai."
sync
echo "Xong."
