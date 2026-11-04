# Convencoes — Qwen30b-Agente
Ultima verificacao: 2026-11-04
- Documentos e prompts em portugues do Brasil, sem acentos nos arquivos de prompt/config (compatibilidade).
- Segredos NUNCA no repositorio: a chave so e escrita em `~/.config/opencode/opencode.json` (chmod 600). `.gitignore` ignora `opencode.json`, backups e `.env`.
- Config: nada de `allow` global para `edit`/`bash "*"`: restricoes ficam POR AGENTE (ver ADR-0001).
- Mudou permissao ou prompt? Rodar `tests/permissions.sh` (com `XDG_CONFIG_HOME` apontando para uma config instalada em /tmp) antes de publicar.
- Relatorios: cada afirmacao como Verificado/Testado/Nao testado/Bloqueado/Suposicao, com evidencia.
- Commits em portugues, descritivos.
