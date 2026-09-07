.PHONY: all build sync init check help install-cli

all: help

build:
	@./scripts/build-distribution.sh

sync:
	@./scripts/sync-harness-configs.sh

init:
	@./bin/clube-config init

check:
	@./bin/clube-config check

install-cli:
	@./bin/clube-config install

help:
	@echo "Available targets in Makefile:"
	@echo "  make build       - Generates multi-harness distribution bundles (omp, claude-code, cursor, etc.)"
	@echo "  make sync        - Syncs harness pointer files (@AGENTS.md) across project directories"
	@echo "  make init        - Runs project AI onboarding and harness configuration"
	@echo "  make check       - Audits active harness configuration and AGENTS.md integrity"
	@echo "  make install-cli - Installs clube-config CLI into ~/.local/bin"
