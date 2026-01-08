# Makefile for Quarm Charm Calculator

.PHONY: help scrape-spells update-spells test test-log run docker-build docker-run clean

help:
	@echo "Quarm Charm Calculator - Available Commands"
	@echo ""
	@echo "  make scrape-spells    Scrape charm spell data from pqdi.cc (live)"
	@echo "  make update-spells    Generate charm_spells_data.py from scraped JSON"
	@echo "  make refresh-spells   Full refresh: scrape + update (recommended)"
	@echo "  make test             Run the calculator tests"
	@echo "  make test-log         Test log parser (requires LOG_FILE=/path/to/log)"
	@echo "  make run              Start the development server"
	@echo "  make docker-build     Build the Docker image"
	@echo "  make docker-run       Run the Docker container"
	@echo "  make clean            Clean up build artifacts"
	@echo ""

scrape-spells:
	@echo "Scraping charm spell data from pqdi.cc..."
	@python3 scrape_pqdi_spells.py
	@echo "Done! Spell data saved to pqdi_charm_spells.json"

update-spells:
	@echo "Generating charm_spells_data.py from pqdi_charm_spells.json..."
	@python3 update_charm_spells.py
	@echo "Done! Verifying..."
	@python3 charm_spells_data.py

refresh-spells: scrape-spells update-spells
	@echo ""
	@echo "Spell data fully refreshed from pqdi.cc!"

test:
	@echo "Running calculator tests..."
	@python3 test_calculator.py

test-log:
	@if [ -z "$(LOG_FILE)" ]; then \
		echo "Usage: make test-log LOG_FILE=/path/to/eqlog.txt"; \
		exit 1; \
	fi
	@echo "Analyzing log file: $(LOG_FILE)"
	@python3 log_parser.py "$(LOG_FILE)"

run:
	@echo "Starting development server..."
	@./start.sh

docker-build:
	@echo "Building Docker image..."
	@cd docker && docker build -f Dockerfile -t quarm-charm-calculator:latest ..

docker-run:
	@echo "Running Docker container..."
	@docker run -d -p 5000:5000 --name charm-calculator quarm-charm-calculator:latest
	@echo "Container started! Access at http://localhost:5000"
	@echo "To stop: docker stop charm-calculator && docker rm charm-calculator"

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	@rm -f *.log 2>/dev/null || true
	@echo "Cleanup complete!"

