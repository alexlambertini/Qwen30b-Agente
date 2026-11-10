// Instalador Windows do ambiente de agentes OpenCode (Qwen3-Coder). Duplo clique ou: qwen-agente-setup.exe --key X [--url U] [--comfyui C]
package main

import (
	"bufio"
	"embed"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

//go:embed all:payload
var payload embed.FS

func say(f string, a ...any) { fmt.Printf("==> "+f+"\n", a...) }
func die(f string, a ...any) {
	fmt.Printf("[erro] "+f+"\n", a...)
	pause()
	os.Exit(1)
}
func pause() {
	fmt.Print("\nPressione Enter para fechar...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}
func ask(q string) string {
	fmt.Print(q)
	s, _ := bufio.NewReader(os.Stdin).ReadString('\n')
	return strings.TrimSpace(s)
}
func copyFile(src, dst string, mode os.FileMode) {
	b, err := os.ReadFile(src)
	if err != nil {
		return
	}
	os.MkdirAll(filepath.Dir(dst), 0o755)
	os.WriteFile(dst, b, mode)
}

func main() {
	url := flag.String("url", "", "URL da API (ex.: http://100.94.64.97:8081/v1)")
	key := flag.String("key", "", "API key")
	comfy := flag.String("comfyui", "", "URL do ComfyUI (ex.: http://100.94.64.97:8188)")
	flag.Parse()
	home, _ := os.UserHomeDir()
	conf := os.Getenv("OPENCODE_CONFIG_DIR")
	if conf == "" {
		conf = filepath.Join(home, ".config", "opencode")
	}
	bin := filepath.Join(home, ".local", "bin")
	interactive := *key == ""

	// instalacao existente: reaproveita o que nao for informado
	oldJSON := filepath.Join(conf, "opencode.json")
	if b, err := os.ReadFile(oldJSON); err == nil {
		var o struct {
			Provider struct {
				Qwen struct {
					Options map[string]any `json:"options"`
				} `json:"qwen"`
			} `json:"provider"`
		}
		if json.Unmarshal(b, &o) == nil {
			if *url == "" {
				*url, _ = o.Provider.Qwen.Options["baseURL"].(string)
			}
			if *key == "" {
				*key, _ = o.Provider.Qwen.Options["apiKey"].(string)
			}
		}
		if *comfy == "" {
			if c, err := os.ReadFile(filepath.Join(conf, "comfyui.url")); err == nil {
				*comfy = strings.TrimSpace(string(c))
			}
		}
		say("Instalacao existente em %s: sera ATUALIZADA (backup automatico; dados mantidos se voce nao informar outros).", conf)
	}
	if *url == "" {
		*url = "https://ia.lambertini.com.br/v1"
		if interactive {
			if v := ask("URL da API [" + *url + "]: "); v != "" {
				*url = v
			}
		}
	}
	if *key == "" {
		*key = ask("API key do servidor Qwen: ")
	}
	if *key == "" {
		die("API key vazia.")
	}
	if *comfy == "" && interactive {
		*comfy = ask("URL do ComfyUI para gerar imagens (Enter = pular): ")
	}
	*url = strings.TrimRight(*url, "/")

	say("Testando %s/models ...", *url)
	req, _ := http.NewRequest("GET", *url+"/models", nil)
	req.Header.Set("Authorization", "Bearer "+*key)
	resp, err := (&http.Client{Timeout: 15 * time.Second}).Do(req)
	if err != nil {
		die("Servidor inacessivel: %v", err)
	}
	resp.Body.Close()
	if resp.StatusCode == 401 || resp.StatusCode == 403 {
		die("Servidor recusou a chave (HTTP %d). Nada foi alterado.", resp.StatusCode)
	}
	say("Servidor respondeu HTTP %d.", resp.StatusCode)

	// backup
	bk := filepath.Join(conf, "backup-"+time.Now().Format("20060102-150405"))
	for _, f := range []string{"opencode.json", "AGENTS.md", "comfyui.url", "prompts/build.md", "prompts/plan.md", "prompts/reviewer.md", "prompts/imagem.md"} {
		copyFile(filepath.Join(conf, f), filepath.Join(bk, f), 0o600)
	}
	if _, err := os.Stat(bk); err == nil {
		say("Backup da configuracao anterior em %s", bk)
	}

	// arquivos embutidos
	fs.WalkDir(payload, "payload", func(p string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() {
			return nil
		}
		rel := strings.TrimPrefix(p, "payload/")
		b, _ := payload.ReadFile(p)
		var dst string
		switch {
		case rel == "opencode.json.tpl":
			var c map[string]any
			json.Unmarshal(b, &c)
			o := c["provider"].(map[string]any)["qwen"].(map[string]any)["options"].(map[string]any)
			o["baseURL"], o["apiKey"] = *url, *key
			b, _ = json.MarshalIndent(c, "", "  ")
			dst = filepath.Join(conf, "opencode.json")
		case strings.HasPrefix(rel, "bin/"):
			dst = filepath.Join(bin, strings.TrimPrefix(rel, "bin/"))
		case strings.HasPrefix(rel, "memory/"):
			dst = filepath.Join(conf, "memory-template", strings.TrimPrefix(rel, "memory/"))
		default:
			dst = filepath.Join(conf, rel) // AGENTS.md, prompts/*
		}
		os.MkdirAll(filepath.Dir(dst), 0o755)
		os.WriteFile(dst, b, 0o644)
		return nil
	})
	os.Chmod(oldJSON, 0o600)
	if *comfy != "" {
		os.WriteFile(filepath.Join(conf, "comfyui.url"), []byte(strings.TrimRight(*comfy, "/")+"\n"), 0o644)
	}
	// qwen-imagem.cmd (o script e Python): chama o python do Windows
	os.WriteFile(filepath.Join(bin, "qwen-imagem.cmd"), []byte("@echo off\r\npython \"%~dp0qwen-imagem\" %*\r\n"), 0o644)
	// bin no PATH do usuario
	ps := `$b='` + bin + `';$p=[Environment]::GetEnvironmentVariable('Path','User');if(($p -split ';') -notcontains $b){[Environment]::SetEnvironmentVariable('Path',($p.TrimEnd(';')+';'+$b),'User')}`
	exec.Command("powershell", "-NoProfile", "-Command", ps).Run()

	say("Pronto. Configuracao em %s", conf)
	fmt.Println("  Agentes : build (padrao), plan, reviewer, explore, imagem")
	fmt.Println("  Workflow: /feature -> /implement -> /review   |   /memoria   |   /imagine <descricao> [4k]")
	if _, err := exec.LookPath("opencode"); err != nil {
		fmt.Println("  Falta o OpenCode: instale em https://opencode.ai e abra um terminal novo.")
	}
	if _, err := exec.LookPath("python"); err != nil {
		fmt.Println("  Para /imagine instale o Python 3 (https://python.org). Abra um terminal novo depois.")
	}
	if interactive {
		pause()
	}
}
