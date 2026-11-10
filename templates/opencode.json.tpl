{
  "$schema": "https://opencode.ai/config.json",
  "model": "qwen/qwen3-coder-30b-a3b",
  "small_model": "qwen/qwen3-coder-30b-a3b",
  "default_agent": "build",
  "instructions": [
    ".opencode/memory/architecture.md",
    ".opencode/memory/conventions.md",
    ".opencode/memory/known-issues.md"
  ],
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 8192
  },
  "experimental": {
    "todo": true
  },
  "permission": {
    "bash": {
      "ssh *": "ask",
      "scp *": "ask",
      "sudo *": "ask",
      "git push *": "ask",
      "rm -rf *": "deny",
      "pip install *": "ask",
      "pip3 install *": "ask",
      "python3 -m pip *": "ask",
      "python -m pip *": "ask",
      "npm install*": "ask",
      "npm i *": "ask",
      "pnpm add *": "ask",
      "yarn add *": "ask",
      "apt *": "ask",
      "apt-get *": "ask",
      "dnf *": "ask",
      "brew install *": "ask"
    }
  },
  "agent": {
    "build": {
      "mode": "primary",
      "description": "Executa o desenvolvimento: le, edita, cria arquivos e roda testes.",
      "steps": 80,
      "prompt": "{file:./prompts/build.md}"
    },
    "plan": {
      "mode": "primary",
      "description": "Investiga e planeja. Somente leitura.",
      "steps": 40,
      "prompt": "{file:./prompts/plan.md}",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "deny",
          "ls *": "allow",
          "cat *": "allow",
          "head *": "allow",
          "tail *": "allow",
          "grep *": "allow",
          "rg *": "allow",
          "find *": "allow",
          "wc *": "allow",
          "pwd": "allow",
          "git status*": "allow",
          "git log*": "allow",
          "git diff*": "allow",
          "git show*": "allow",
          "git blame*": "allow"
        },
        "task": {
          "*": "deny",
          "explore": "allow"
        }
      }
    },
    "reviewer": {
      "mode": "subagent",
      "description": "Revisao tecnica independente. Nao edita nem executa comandos.",
      "steps": 30,
      "prompt": "{file:./prompts/reviewer.md}",
      "permission": {
        "edit": "deny",
        "bash": "deny",
        "task": {
          "*": "deny",
          "explore": "allow"
        }
      }
    },
    "imagem": {
      "mode": "subagent",
      "description": "Gera imagens (SDXL via ComfyUI), inclusive em 4K. Use quando o usuario pedir para criar/gerar uma imagem, ilustracao, icone, banner ou wallpaper.",
      "steps": 8,
      "prompt": "{file:./prompts/imagem.md}",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "deny",
          "~/.local/bin/qwen-imagem *": "allow",
          "qwen-imagem *": "allow"
        },
        "task": {
          "*": "deny"
        }
      }
    },
    "explore": {
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "deny",
          "ls *": "allow",
          "cat *": "allow",
          "head *": "allow",
          "tail *": "allow",
          "grep *": "allow",
          "rg *": "allow",
          "find *": "allow",
          "wc *": "allow",
          "pwd": "allow",
          "git status*": "allow",
          "git log*": "allow",
          "git diff*": "allow",
          "git show*": "allow",
          "git blame*": "allow"
        }
      }
    },
    "web": {
      "mode": "primary",
      "description": "Especialista em layout web: HTML/CSS responsivo, acessibilidade e verificacao automatica em 3 larguras.",
      "steps": 80,
      "prompt": "{file:./prompts/web.md}"
    }
  },
  "provider": {
    "qwen": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Qwen3-Coder-30B-A3B (servidor remoto)",
      "options": {
        "baseURL": "__BASE_URL__",
        "apiKey": "__API_KEY__"
      },
      "models": {
        "qwen3-coder-30b-a3b": {
          "name": "Qwen3-Coder-30B-A3B-Instruct",
          "tool_call": true,
          "reasoning": false,
          "options": {
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 20,
            "repeat_penalty": 1.05
          },
          "limit": {
            "context": 98304,
            "output": 8192
          }
        }
      }
    }
  },
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "oauth": false
    }
  },
  "commands": {
    "imagine": {
      "description": "Gera uma imagem com o ComfyUI (acrescente '4k' para alta resolucao)",
      "agent": "imagem",
      "template": "Gere a imagem: $ARGUMENTS"
    },
    "feature": {
      "description": "Passo 1 do workflow: investigar e planejar (somente leitura)",
      "agent": "plan",
      "template": "Planeje a seguinte demanda e pare para aprovacao: $ARGUMENTS\n\nPrimeiro faca o Passo 0 do seu prompt (projeto existente ou novo). Se for projeto NOVO, projete (requisitos, stack, arquitetura em camadas, modelagem com checklist de entidades transversais, estrutura de diretorios, etapas); nao procure o que 'atualizar'. Siga o formato de entrega e termine com 'Autoriza a execucao pelo Build?'."
    },
    "implement": {
      "description": "Passo 2: executar o plano aprovado (Build)",
      "agent": "build",
      "template": "Execute o PLANO APROVADO acima nesta conversa (ou, se foi dado aqui: $ARGUMENTS). Escopo: somente o que o plano lista; nao reescreva codigo existente nem troque de framework/estilo. Ao final gere .opencode/review/status.txt e diff.patch e entregue o relatorio."
    },
    "review": {
      "description": "Passo 3: revisao independente (Reviewer, sem edit/bash)",
      "agent": "reviewer",
      "template": "Revise a mudanca nao commitada deste repositorio. Escopo aprovado: $ARGUMENTS. Leia .opencode/review/status.txt e diff.patch, depois os arquivos reais, e confira CADA regra de .opencode/memory/conventions.md na tabela de conformidade."
    },
    "memoria": {
      "description": "Cria/atualiza .opencode/memory/ do projeto a partir do codigo real",
      "agent": "build",
      "template": "Crie (ou atualize, sem apagar decisoes) a memoria persistente deste projeto em .opencode/memory/, baseada SOMENTE no que voce verificar no codigo e na configuracao reais (leia README, manifestos de dependencia, estrutura de diretorios, testes). Arquivos: architecture.md (visao geral, componentes+caminhos, fluxos, dependencias com versao, como rodar/testar), conventions.md (padroes de codigo, diretorios, nomes, estrategia de testes com comando, regras especificas; liste cada regra numerada e verificavel), known-issues.md (tabela de problemas reais encontrados, com evidencia), decisions/ e tasks/ (crie com um arquivo _TEMPLATE.md simples se nao existirem). Seja curto e factual; marque 'Suposicao' o que nao verificou. Mostre ao final a lista de arquivos criados. Contexto adicional do usuario: $ARGUMENTS"
    },
    "web": {
      "description": "Cria/ajusta uma pagina web responsiva e verifica o layout",
      "agent": "web",
      "template": "$ARGUMENTS"
    }
  }
}
