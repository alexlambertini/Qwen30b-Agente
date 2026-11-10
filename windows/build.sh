#!/usr/bin/env bash
# Gera dist/qwen-agente-setup.exe (Windows 64 bits) com os templates embutidos. Requer Go.
set -e; cd "$(dirname "$0")"; R=..
rm -rf payload; mkdir -p payload
cp -r $R/templates/prompts payload/; cp -r $R/templates/bin payload/; cp -r $R/templates/memory payload/
cp $R/templates/AGENTS.md $R/templates/opencode.json.tpl payload/
[ -f go.mod ] || go mod init qwen-agente-setup >/dev/null 2>&1
mkdir -p $R/dist; GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o $R/dist/qwen-agente-setup.exe .
rm -rf payload; ls -la $R/dist/qwen-agente-setup.exe
