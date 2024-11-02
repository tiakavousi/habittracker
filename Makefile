VENV_DIR = .venv
PYTHON = python3
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip
PROJECT_NAME = habit_tracker
SRC_DIR = src

ifeq ($(OS),Windows_NT)
	VENV_PYTHON = $(VENV_DIR)/Scripts/python
	VENV_PIP = $(VENV_DIR)/Scripts/pip
	ACTIVATE = . $(VENV_DIR)/Scripts/activate
	RM_CMD = rmdir /s /q
else
	ACTIVATE = . $(VENV_DIR)/bin/activate
	RM_CMD = rm -rf
endif

.PHONY: all clean install run test venv setup

all: venv install setup

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created."

install: venv
	@echo "Installing dependencies..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -e .
	@echo "Dependencies installed."

setup:
	@echo "Setting up environment..."
	@echo "export PYTHONPATH=$(SRC_DIR):$$PYTHONPATH" > $(VENV_DIR)/bin/postactivate
	@echo "Creating habit-tracker command..."
	@echo '#!/bin/bash' > $(VENV_DIR)/bin/habit-tracker
	@echo 'PYTHONPATH=$(SRC_DIR) python -m habit_tracker.cli "$$@"' >> $(VENV_DIR)/bin/habit-tracker
	@chmod +x $(VENV_DIR)/bin/habit-tracker
	@echo "Setup complete. Use '' to activate the environment."
	@echo "Setup complete. Use 'source $(VENV_DIR)/bin/activate' to activate the environment."

run: install
	@echo "Running Habit Tracker..."
	@$(VENV_PYTHON) -m $(PROJECT_NAME).cli

test: install
	@echo "Running tests..."
	@PYTHONPATH=$(SRC_DIR) $(VENV_PYTHON) -m pytest tests/

clean:
	@echo "Cleaning up..."
	@$(RM_CMD) $(VENV_DIR) 2>/dev/null || true
	@$(RM_CMD) *.egg-info 2>/dev/null || true
	@$(RM_CMD) __pycache__ 2>/dev/null || true
	@$(RM_CMD) .pytest_cache 2>/dev/null || true
	@$(RM_CMD) .coverage 2>/dev/null || true
	@$(RM_CMD) build/ 2>/dev/null || true
	@$(RM_CMD) dist/ 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "*.db" -delete 2>/dev/null || true
	@echo "Cleanup complete."

help:
	@echo "Available targets:"
	@echo "  make          : Create venv and install dependencies"
	@echo "  make install  : Install dependencies in virtual environment"
	@echo "  make run     : Run the application"
	@echo "  make test    : Run tests"
	@echo "  make clean   : Remove virtual environment and cleanup"
	@echo "  make help    : Show this help message"