"""使用真实LLM API测试小说创作"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.pipeline.novel_pipeline import NovelPipeline
from src.models.dashscope_model import DashScopeModel
from src.tools.storage import Storage


async def test_novel_creation():
    """测试小说创作流程"""
    
    print("=" * 60)
    print("开始测试小说创作流程")
    print("=" * 60)
    
    # 初始化 DashScope 模型
    try:
        model = DashScopeModel()
        print(f"✓ 模型初始化成功: {model.model_name}")
        print(f"✓ API Base URL: {model.base_url}")
    except ValueError as e:
        print(f"✗ 模型初始化失败: {e}")
        return
    
    # 创建小说流水线
    output_dir = Path("data/novels/test_llm")
    pipeline = NovelPipeline(
        model=model,
        output_dir=str(output_dir),
        config={
            "num_characters": 3,
            "era": "现代"
        }
    )
    
    # 确保storage的base_dir与output_dir一致
    pipeline.storage.base_dir = Path("data")
    
    # 步骤1: 创建小说项目
    print("\n" + "-" * 60)
    print("步骤1: 创建小说项目")
    print("-" * 60)
    
    novel_id = await pipeline.create_novel(
        title="AI的觉醒",
        theme="人工智能获得自我意识后的故事",
        genre="科幻",
        style="硬科幻，哲学思考",
        num_chapters=3
    )
    print(f"✓ 小说项目创建成功，ID: {novel_id}")
    
    # 步骤2: 生成小说大纲
    print("\n" + "-" * 60)
    print("步骤2: 生成小说大纲")
    print("-" * 60)
    
    try:
        outline = await pipeline.generate_outline()
        print(f"✓ 大纲生成成功")
        print(f"\n大纲预览:")
        print(outline.get("plot_outline", "")[:500] + "...")
    except Exception as e:
        print(f"✗ 大纲生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤3: 生成角色设定
    print("\n" + "-" * 60)
    print("步骤3: 生成角色设定")
    print("-" * 60)
    
    try:
        characters = await pipeline.generate_characters()
        print(f"✓ 角色生成成功")
        print(f"\n角色数量: {len(characters.get('characters', []))}")
        if characters.get('protagonist'):
            print(f"主角: {characters['protagonist'].get('name', '未知')}")
    except Exception as e:
        print(f"✗ 角色生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤4: 生成世界观设定
    print("\n" + "-" * 60)
    print("步骤4: 生成世界观设定")
    print("-" * 60)
    
    try:
        world = await pipeline.generate_world()
        print(f"✓ 世界观生成成功")
        print(f"\n世界观预览:")
        print(world.get("world_description", "")[:500] + "...")
    except Exception as e:
        print(f"✗ 世界观生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤5: 写作第一章
    print("\n" + "-" * 60)
    print("步骤5: 写作第一章")
    print("-" * 60)
    
    try:
        chapter1 = await pipeline.write_chapter(1)
        print(f"✓ 第一章写作完成")
        print(f"字数: {chapter1.get('word_count', 0)}")
        print(f"\n章节预览:")
        content = chapter1.get("edited_content", chapter1.get("content", ""))
        print(content[:800] + "...")
    except Exception as e:
        print(f"✗ 第一章写作失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤6: 导出小说
    print("\n" + "-" * 60)
    print("步骤6: 导出小说")
    print("-" * 60)
    
    try:
        export_path = await pipeline.export_novel()
        print(f"✓ 小说导出成功")
        print(f"导出路径: {export_path}")
    except Exception as e:
        print(f"✗ 小说导出失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("小说创作测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("LLM_API_KEY"):
        print("错误: 未设置 LLM_API_KEY 环境变量")
        print("请确保 .env 文件存在且包含正确的 API 密钥")
        exit(1)
    
    # 运行测试
    asyncio.run(test_novel_creation())
