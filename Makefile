setup:
	@echo "[*] Initializing ZTAA RADIUS Diagnostic Suite Setup..."
	@if ! command -v python3 > /dev/null; then \
		echo "[!] Python3 is not installed. Attempting automatic installation..."; \
		if command -v apt > /dev/null; then \
			sudo apt update && sudo apt install -y python3 python3-venv python3-pip; \
		elif command -v yum > /dev/null; then \
			sudo yum install -y python3 python3-pip; \
		elif command -v brew > /dev/null; then \
			brew install python; \
		else \
			echo "[FATAL] Could not find a supported package manager. Please install Python3 manually."; \
			exit 1; \
		fi; \
	fi
	@echo "[*] Setting up local environment..."
	@python3 -m venv venv
	@./venv/bin/pip install -r requirements.txt -q
	@echo "[*] Setup complete. Type 'make RADIUS' to start."

RADIUS:
	@echo "[*] Launching Diagnostic Console..."
	@./venv/bin/python app.py