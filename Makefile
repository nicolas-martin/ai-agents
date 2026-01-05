# Makefile for Chart Analysis Agent

.PHONY: run polymarket install clean help

# Default target
.DEFAULT_GOAL := help

# Run the chart analysis agent
run:
	@echo "Activating conda environment: tflow"
	@bash -c "python -m src.agents.chartanalysis_agent"

# Run the polymarket agent
polymarket:
	@bash -c "python -m src.agents.polymarket_agent"

# Install dependencies
install:
	pip install -r requirements.txt

# Clean generated files (charts and audio)
clean:
	rm -rf src/data/charts/*
	rm -rf src/audio/*

# Show help
help:
	@echo "AI Agents - Available targets:"
	@echo ""
	@echo "  make run        - Run the chart analysis agent"
	@echo "  make polymarket - Run the polymarket agent"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Remove generated charts and audio files"
	@echo "  make help       - Show this help message"
