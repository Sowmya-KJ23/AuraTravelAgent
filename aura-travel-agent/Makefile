.PHONY: install playground generate-traces grade

install:
	agents-cli install

playground:
	agents-cli playground

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	agents-cli eval grade --traces artifacts/traces/basic-traces.json --config tests/eval/eval_config.yaml
