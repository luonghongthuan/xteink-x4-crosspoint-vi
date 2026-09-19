#!/usr/bin/env bash
# Day sach tu Mac sang Kindle (KOReader) qua WiFi — khong can cap USB.
# Tren Kindle: KOReader -> cong cu -> SSH -> Start SSH server, xem IP hien ra.
#
#   bash tools/kindle-push.sh 192.168.1.25                  # day tat ca .epub trong ~/ebooks
#   bash tools/kindle-push.sh 192.168.1.25 a.epub b.pdf     # day file chi dinh
#
# Dung tar-over-ssh vi dropbear tren Kindle khong co scp/sftp.
set -e
IP="${1:?Thieu IP Kindle. Vd: bash tools/kindle-push.sh 192.168.1.25}"
shift || true
PORT="${KINDLE_PORT:-2222}"
DEST="${KINDLE_DEST:-/mnt/us/documents}"
SRC="$HOME/ebooks"

k() { ssh -p "$PORT" -o ConnectTimeout=8 -o BatchMode=yes "root@$IP" "$@"; }

k "echo ok" >/dev/null 2>&1 || {
  echo "Khong ket noi duoc $IP:$PORT."
  echo "  - Kindle da bat SSH server chua? (restart KOReader la SSH tat)"
  echo "  - Mac va Kindle co cung dai mang khong? (vd cung 192.168.1.x)"
  exit 1
}

files=()
if [ "$#" -gt 0 ]; then
  for f in "$@"; do [ -f "$f" ] && files+=("$f") || echo "  bo qua (khong thay): $f"; done
else
  while IFS= read -r -d '' f; do files+=("$f"); done \
    < <(find "$SRC" -maxdepth 2 \( -iname "*.epub" -o -iname "*.pdf" -o -iname "*.cbz" \) -print0)
fi
[ "${#files[@]}" -eq 0 ] && { echo "Khong co file nao de day."; exit 0; }

echo "Day ${#files[@]} file -> $IP:$DEST"
n=0
for f in "${files[@]}"; do
  base=$(basename "$f")
  COPYFILE_DISABLE=1 tar -C "$(dirname "$f")" -cf - "$base" | k "tar -C '$DEST' -xf -"
  echo "   + $base"
  n=$((n+1))
done
k "sync"
echo "Xong: $n file. Tren Kindle keo xuong de lam moi thu vien."
