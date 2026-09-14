.PHONY: all check audit test sync init help install-cli

all: help

check:
	@./bin/clube-config check

audit:
	@./bin/clube-config audit

test:
	@./bin/clube-config test

sync:
	@./bin/clube-config sync

init:
	@./bin/clube-config init

install-cli:
	@./bin/clube-config install

help:
	@echo "Available targets in Makefile:"
	@echo "  make check       - Audits active harness, marketplace catalogs, and plugin integrity"
	@echo "  make audit       - Runs 360° production audit (privacy, performance, SEO/GEO, tracking)"
	@echo "  make test        - Runs the Python test suite (pytest via uv)"
	@echo "  make sync        - Syncs harness pointer files (@AGENTS.md) across project directories"
	@echo "  make init        - Runs project AI onboarding and harness configuration"
	@echo "  make install-cli - Installs clube-config CLI into ~/.local/bin"
