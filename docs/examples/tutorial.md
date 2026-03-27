# PlotPulse 快速入门教程

## 环境准备

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/plotpulse.git
cd plotpulse

# 安装依赖
pip install -r requirements.txt

# 或使用 pip install -e . 安装为可编辑模式
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
OPENAI_API_KEY=your_api_key_here
```

## 创建你的第一本小说

### 方式一：使用命令行脚本

```bash
# 创建新小说
python scripts/create_novel.py \
  --title "我的第一本AI小说" \
  --theme "成长与冒险" \
  --genre "奇幻" \
  --chapters 10

# 系统会提示你是否立即生成大纲，输入 y
# 然后继续创作
python scripts/continue_writing.py --novel-id <你的小说ID>

# 导出完成的小说
python scripts/export_novel.py --novel-id <你的小说ID> --format md
```

### 方式二：使用Python代码

```python
import asyncio
from src.pipeline import NovelPipeline
from src.models.openai_model import OpenAIModel

async def main():
    # 初始化模型
    model = OpenAIModel(model_name="gpt-4")
    
    # 创建流水线
    pipeline = NovelPipeline(model)
    
    # 创建小说项目
    novel_id = await pipeline.create_novel(
        title="我的第一本AI小说",
        theme="成长与冒险",
        genre="奇幻",
        style="史诗风格",
        num_chapters=10
    )
    print(f"小说项目创建成功，ID: {novel_id}")
    
    # 生成大纲
    outline = await pipeline.generate_outline()
    print("大纲生成完成!")
    
    # 生成角色
    characters = await pipeline.generate_characters()
    print("角色设计完成!")
    
    # 生成世界观
    world = await pipeline.generate_world()
    print("世界观构建完成!")
    
    # 写作所有章节
    await pipeline.write_all_chapters()
    print("所有章节写作完成!")
    
    # 审阅
    review = await pipeline.review_novel()
    print(f"审阅完成，评分: {review['score']}")
    
    # 导出
    filepath = await pipeline.export_novel()
    print(f"小说已导出: {filepath}")

# 运行
asyncio.run(main())
```

## 进阶使用

### 自定义Agent配置

```python
from src.agents import WritingAgent

# 创建自定义配置的写作Agent
writing_agent = WritingAgent(
    model=model,
    config={
        "temperature": 0.9,
        "style": "浪漫主义",
        "word_count_per_chapter": 5000
    }
)
```

### 使用不同的AI模型

```python
from src.models.anthropic_model import AnthropicModel

# 使用Claude模型
model = AnthropicModel(model_name="claude-3-opus-20240229")
```

### 增量创作

```python
# 加载已有项目继续创作
pipeline = NovelPipeline(model)
pipeline.novel_id = "已有的项目ID"
pipeline.novel_data = storage.load_json("metadata.json", "novels/in_progress/novel_xxx")

# 继续写作
await pipeline.write_chapter(5)  # 写作第5章
```

## 项目管理

### 查看所有项目

```bash
ls novels/in_progress/
```

### 分析小说

```bash
python scripts/analyze_novel.py --novel-id <ID>
```

### 导出不同格式

```bash
# Markdown（默认）
python scripts/export_novel.py --novel-id <ID> --format md

# 纯文本
python scripts/export_novel.py --novel-id <ID> --format txt

# HTML
python scripts/export_novel.py --novel-id <ID> --format html
```

## 常见问题

### Q: 如何修改已生成的大纲？

A: 直接编辑 `novels/in_progress/novel_{id}/metadata.json` 中的 `outline` 字段。

### Q: 可以只使用部分Agent吗？

A: 可以！你可以直接实例化需要的Agent并调用：

```python
from src.agents import WritingAgent

agent = WritingAgent(model)
result = await agent.execute({
    "chapter_num": 1,
    "outline": your_outline,
    "characters": your_characters,
    "world": your_world
})
```

### Q: 如何添加自定义提示词？

A: 在 `prompts/system/` 目录添加新的 `.txt` 文件，然后在Agent配置中引用。

## 下一步

- 阅读 [架构设计](../architecture.md) 了解系统原理
- 查看 [API参考](../api-reference.md) 了解详细接口
- 探索 [开发指南](../development-guide.md) 学习如何扩展功能
