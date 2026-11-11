#!/bin/zsh
# Uso: [CAPDIR=subcarpeta] cap.sh NOMBRE 'comando' ...  -> guarda prompt+comando+salida real en caps/NOMBRE.txt
S="${0:A:h}"
LAB="${S:h}"
mkdir -p "$S/evidencias"
name=$1; shift
out="$S/evidencias/$name.txt"
: > "$out"
cd "$LAB/${CAPDIR:-}"
export AWS_PAGER=""
if [ -z "$CAPDIR" ]; then
  export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 EP=http://localhost:4566
else
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE
fi
for c in "$@"; do
  printf "\033[1;32m%s@%s\033[0m \033[1;34m%s\033[0m %% %s\n" "$USER" "$(scutil --get LocalHostName 2>/dev/null || hostname -s)" "${PWD:t}" "$c" >> "$out"
  zsh -c "$c" >> "$out" 2>&1
done
cat "$out"
