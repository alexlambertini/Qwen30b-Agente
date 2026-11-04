{
  "$schema": "https://opencode.ai/config.json",
  "model": "qwen/qwen3-coder-30b-a3b",
  "small_model": "qwen/qwen3-coder-30b-a3b",
  "default_agent": "build",
  "compaction": { "auto": true, "prune": true, "reserved": 8192 },

  "permission": {
    "bash": {
      "ssh *": "ask",
      "scp *": "ask",
      "sudo *": "ask",
      "git push *": "ask",
      "rm -rf *": "deny"
    }
  },

  "agent": {
    "build": {
      "mode": "primary",
      "description": "Executa o desenvolvimento: le, edita, cria arquivos e roda testes.",
      "temperature": 0.3,
      "prompt": "{file:./prompts/build.md}"
    },
    "plan": {
      "mode": "primary",
      "description": "Investiga e planeja. Somente leitura.",
      "temperature": 0.3,
      "prompt": "{file:./prompts/plan.md}",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "deny",
          "ls *": "allow", "cat *": "allow", "head *": "allow", "tail *": "allow",
          "grep *": "allow", "rg *": "allow", "find *": "allow", "wc *": "allow", "pwd": "allow",
          "git status*": "allow", "git log*": "allow", "git diff*": "allow", "git show*": "allow"
        }
      }
    },
    "reviewer": {
      "mode": "subagent",
      "description": "Revisao tecnica independente. Nao edita nem executa comandos.",
      "temperature": 0.2,
      "prompt": "{file:./prompts/reviewer.md}",
      "permission": { "edit": "deny", "bash": "deny" }
    },
    "explore": {
      "permission": { "edit": "deny", "bash": "deny" }
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
          "limit": { "context": 98304, "output": 8192 }
        }
      }
    }
  }
}
