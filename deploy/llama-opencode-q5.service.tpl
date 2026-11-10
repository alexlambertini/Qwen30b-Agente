[Unit]
StartLimitIntervalSec=300
StartLimitBurst=3
Description=llama-server OpenCode (Qwen3-Coder-30B-A3B Q5_K_M, RTX 3090 + sobra na 3060 #2)
After=network.target

[Service]
Type=simple
User=lambertini
Environment="CUDA_VISIBLE_DEVICES=GPU-62db84a1-2382-5e24-e65c-2cd9c91d4390,GPU-06b9f913-ecbb-04d0-3de8-e8ae9c872379"
Environment="LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64"
ExecStart=/srv/llama.cpp/build/bin/llama-server \
  --model /srv/models/Qwen3-Coder-30B-A3B-Instruct-Q5_K_M.gguf \
  --alias qwen3-coder-30b-a3b \
  --gpu-layers all \
  --split-mode layer \
  --tensor-split @@TS@@ \
  --ctx-size @@CTX@@ \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --threads 2 \
  --threads-batch 2 \
  --flash-attn on \
  --jinja \
  --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 \
  --cache-ram 512 \
  --host 100.94.64.97 \
  --port 8081 \
  --api-key @@KEY@@ \
  --parallel 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
