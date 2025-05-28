.DEFAULT_GOAL := help
DOCS=$(wildcard *.md) $(wildcard **/*.md)

.PHONY: ci-lint
ci-lint:  ## Lint GitHub Actions workflows.
	@poetry run zizmor .

.PHONY: docs-lint
docs-lint: $(DOCS)  ## Lint Markdown-format documentation.
	@npx prettier --check $^

.PHONY: fix
docs-fix: $(DOCS)  ## Apply automatic fixes to Markdown-format documentation.
	@npx prettier --write $^

.PHONY: doxygen
doxygen:  ## Generate browsable documentation and call/caller graphs (requires Doxygen and Graphviz).
	@which doxygen >> /dev/null || { echo "doxygen(1) is not available in your \$$PATH.  Is it installed?"; exit 1; }
	@which dot >> /dev/null || { echo "Graphviz's dot(1) is not available in your \$$PATH.  Is it installed?"; exit 1; }
	@doxygen
	@echo "Now open \"$(PWD)/docs/html/index.html\" in your browser."

.PHONY: fix
fix: docs-fix  ## Apply automatic fixes.

.PHONY: lint
lint: ci-lint docs-lint  ## Run all linters.

.PHONY: help
help: ## Prints this message and exits.
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t
