# PlotPulse 📝🤖

一个基于AI的多Agent协作小说创作框架

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 特性

- 🤖 **多Agent协作** - 情节、角色、世界观、写作、编辑、审阅各司其职
- 📝 **端到端创作** - 从构思到成品的完整创作流程
- 🎨 **高度可扩展** - 模块化设计，易于定制和扩展
- 📚 **作品管理** - 系统化的小说项目管理
- 🔌 **多模型支持** - 支持OpenAI、Anthropic Claude及本地模型

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/plotpulse.git
cd plotpulse

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的API密钥
```

### 创建你的第一本小说

```bash
# 使用命令行
python scripts/create_novel.py \
  --title "我的AI小说" \
  --theme "科幻冒险" \
  --genre "科幻" \
  --chapters 10

# 继续创作
python scripts/continue_writing.py --novel-id <ID>

# 导出成品
python scripts/export_novel.py --novel-id <ID>
```

或使用Python代码：

```python
import asyncio
from src.pipeline import NovelPipeline
from src.models.openai_model import OpenAIModel

async def main():
    model = OpenAIModel()
    pipeline = NovelPipeline(model)
    
    # 创建项目
    novel_id = await pipeline.create_novel(
        title="我的AI小说",
        theme="科幻冒险",
        genre="科幻",
        num_chapters=10
    )
    
    # 完整创作流程
    await pipeline.generate_outline()
    await pipeline.generate_characters()
    await pipeline.generate_world()
    await pipeline.write_all_chapters()
    
    # 导出
    await pipeline.export_novel()

asyncio.run(main())
```

## 📁 项目结构

```
plotpulse/
├── src/                    # 源代码
│   ├── core/              # 核心框架
│   ├── agents/            # 创作Agent
│   ├── models/            # AI模型封装
│   ├── tools/             # 工具函数
│   └── pipeline/          # 创作流水线
├── novels/                # 小说作品
│   ├── in_progress/       # 创作中
│   ├── published/         # 已完成
│   └── archived/          # 归档
├── prompts/               # 提示词库
├── config/                # 配置文件
├── scripts/               # 实用脚本
├── tests/                 # 测试
└── docs/                  # 文档
```

## 🏗️ 架构

PlotPulse 采用多Agent协作架构：

```
用户输入 → 情节设计Agent → 角色设计Agent → 世界观Agent → 
写作Agent → 编辑Agent → 审阅Agent → 成品输出
```

每个Agent专注于创作流程的一个环节，通过流水线协调工作。

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
make test

# 代码格式化
make format

# 代码检查
make lint
```

## 📖 文档

- [快速开始](docs/examples/tutorial.md)
- [架构设计](docs/architecture.md)
- [API参考](docs/api-reference.md)
- [开发指南](docs/development-guide.md)

## 🤝 贡献

欢迎贡献代码！请阅读[贡献指南](CONTRIBUTING.md)了解如何参与。

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- OpenAI GPT-4
- Anthropic Claude
- 所有贡献者

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
