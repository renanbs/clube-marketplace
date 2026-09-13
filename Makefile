.PHONY: all check audit sync init help install-cli

all: help

check:
	@./bin/clube-config check

audit:
	@./bin/clube-config audit

sync:
	@./scripts/sync-harness-configs.sh

init:
	@./bin/clube-config init

install-cli:
	@./bin/clube-config install

help:
	@echo "Available targets in Makefile:"
	@echo "  make check       - Audits active harness, marketplace catalogs, and plugin integrity"
	@echo "  make audit       - Runs 360° production audit (privacy, performance, SEO/GEO, tracking)"
	@echo "  make sync        - Syncs harness pointer files (@AGENTS.md) across project directories"
	@echo "  make init        - Runs project AI onboarding and harness configuration"
	@echo "  make install-cli - Installs clube-config CLI into ~/.local/bin"
