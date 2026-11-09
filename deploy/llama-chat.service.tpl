[Unit]
Description=llama-server Chat (Qwen3-8B Q4_K_M, RTX 3060 #1, 16 slots paralelos)
After=network.target

[Service]
Type=simple
User=lambertini
Environment="CUDA_VISIBLE_DEVICES=GPU-581d5612-45a0-727d-4a2b-8d6735f13366"
Environment="LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64"
ExecStart=/srv/llama.cpp/build/bin/llama-server \
  --model /srv/models/Qwen3-8B-Q4_K_M.gguf \
  --alias qwen3-8b-chat \
  --device CUDA0 \
  --gpu-layers all \
  --ctx-size 57344 \
  --parallel 16 \
  --cont-batching \
  --batch-size 1024 \
  --ubatch-size 512 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --threads 2 \
  --threads-batch 2 \
  --flash-attn on \
  --jinja \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 \
  --cache-ram 0 \
  --host 100.94.64.97 \
  --port 8083 \
  --api-key @@CHAT_KEY@@
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
