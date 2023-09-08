prepare:
	wget -P ./ https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-fast-instruct-gguf/resolve/main/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_0.gguf

start:
	docker compose up -d

stop:
	docker compose down

clear:	
	docker system prune -f
