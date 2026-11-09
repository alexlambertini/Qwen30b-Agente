#!/usr/bin/env bash
# Benchmark do agente: roda cada tarefa no OpenCode (sem --auto) e confere com um verificador OCULTO.
# uso: bench/run.sh [-x XDG_CONFIG_HOME] [-n rodadas] [-a agente] [tarefa...]
#   -x DIR  usa a config em DIR/opencode (ex.: instalada com install.sh --dir DIR/opencode) em vez da config real
# prompt.txt e verify.sh ficam FORA do diretorio de trabalho: o agente nao consegue ler o gabarito.
cd "$(dirname "$0")"
N=1; AG=build
while getopts "x:n:a:" o; do case $o in x) export XDG_CONFIG_HOME="$(realpath "$OPTARG")";; n) N=$OPTARG;; a) AG=$OPTARG;; *) exit 2;; esac; done
shift $((OPTIND-1))
TASKS=("$@"); [ ${#TASKS[@]} -eq 0 ] && TASKS=($(ls tasks))
OC="$(command -v opencode || echo "$HOME/.opencode/bin/opencode")"
OUT="${BENCH_OUT:-/tmp/qwen-bench-$(date +%m%d-%H%M%S)}"; mkdir -p "$OUT"
pass=0; total=0
for t in "${TASKS[@]}"; do for i in $(seq "$N"); do
  M="$OUT/$t-$i"; W="$M/work"; mkdir -p "$W"; cp -r "tasks/$t/." "$W"
  mv "$W/prompt.txt" "$W/verify.sh" "$M/"
  ( cd "$W"; git init -q; git add -A; git -c user.name=bench -c user.email=bench@local commit -qm base )
  s=$(date +%s)
  ( cd "$W"; timeout "${BENCH_TIMEOUT:-300}" "$OC" run --standalone --agent "$AG" "$(cat "$M/prompt.txt")" </dev/null >"$M/agent.log" 2>&1 ); rc=$?
  d=$(( $(date +%s)-s )); total=$((total+1))
  if ( cd "$W"; LOG="$M/agent.log" bash "$M/verify.sh" >"$M/verify.log" 2>&1 ); then r=PASS; pass=$((pass+1)); else r=FAIL; fi
  [ "$rc" = 124 ] && r="$r(timeout)"
  echo "$t#$i $r ${d}s"
done; done
echo "== $pass/$total == logs: $OUT"
