# PlotPulse Makefile

.PHONY: help install install-dev test lint format clean run

help:
	@echo "PlotPulse 可用命令:"
	@echo "  make install      - 安装生产依赖"
	@echo "  make install-dev  - 安装开发依赖"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 运行代码检查"
	@echo "  make format       - 格式化代码"
	@echo "  make clean        - 清理缓存文件"
	@echo "  make create-novel - 创建新小说"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/

create-novel:
	@read -p "小说标题: " title; \
	read -p "主题: " theme; \
	read -p "类型: " genre; \
	python scripts/create_novel.py --title "$$title" --theme "$$theme" --genre "$$genre"

continue:
	@read -p "小说ID: " id; \
	python scripts/continue_writing.py --novel-id "$$id"

export:
	@read -p "小说ID: " id; \
	read -p "格式 (md/txt/html): " fmt; \
	python scripts/export_novel.py --novel-id "$$id" --format "$$fmt"

analyze:
	@read -p "小说ID: " id; \
	python scripts/analyze_novel.py --novel-id "$$id"
