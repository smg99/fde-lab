.PHONY: venv install demo test lint clean js-install js-build js-test pack-demo

venv:
	python3 -m venv venv

install: venv js-install
	./venv/bin/pip install -e ".[dev]"

demo:
	./venv/bin/python -m demo.run

test: js-test
	./venv/bin/pytest tests/ -v

lint:
	./venv/bin/black fde_lab tests demo
	./venv/bin/isort fde_lab tests demo
	./venv/bin/mypy fde_lab

js-install:
	npm install

js-build: js-install
	npm run build

js-test: js-build
	npm test

pack-demo: js-build
	@echo "Packing JS packages for local testing..."
	@cd packages/cli-core && npm pack
	@cd packages/environment-inspector && npm pack
	@cd packages/incident-engineer && npm pack
	@cd packages/integration-engineer && npm pack
	@cd packages/deployment-engineer && npm pack
	@rm -rf test-npx-env
	@mkdir test-npx-env
	@mv packages/cli-core/*.tgz test-npx-env/
	@mv packages/environment-inspector/*.tgz test-npx-env/
	@mv packages/incident-engineer/*.tgz test-npx-env/
	@mv packages/integration-engineer/*.tgz test-npx-env/
	@mv packages/deployment-engineer/*.tgz test-npx-env/
	@echo "Local packages ready in test-npx-env/. To test locally:"
	@echo "  npm install -g ./test-npx-env/fde-lab-cli-core-0.1.4.tgz"
	@echo "  npm install -g ./test-npx-env/fde-lab-incident-engineer-0.1.4.tgz"
	@echo "  npm install -g ./test-npx-env/fde-lab-integration-engineer-0.1.0.tgz"
	@echo "  npm install -g ./test-npx-env/fde-lab-deployment-engineer-0.1.0.tgz"
	@echo "  fde-incident-engineer"
	@echo "  fde-integration-engineer"
	@echo "  fde-deployment-engineer"
	cd test-npx-env && npx fde-environment-inspector < /dev/null || true
	cd test-npx-env && npx fde-incident-engineer < /dev/null || true
	cd test-npx-env && npx fde-incident-engineer --scenario inconclusive < /dev/null || true

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf venv
	rm -rf node_modules packages/*/node_modules packages/*/dist
	rm -rf test-npx-env
