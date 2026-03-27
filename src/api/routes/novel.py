"""小说相关路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/novels", tags=["novels"])


class NovelCreateRequest(BaseModel):
    title: str
    theme: str
    genre: str
    style: Optional[str] = ""
    num_chapters: int = 10


class NovelResponse(BaseModel):
    id: str
    title: str
    theme: str
    genre: str
    status: str
    created_at: str


@router.post("/", response_model=NovelResponse)
async def create_novel(request: NovelCreateRequest):
    """创建新小说项目"""
    # TODO: 实现创建逻辑
    return {
        "id": "test-id",
        "title": request.title,
        "theme": request.theme,
        "genre": request.genre,
        "status": "created",
        "created_at": "2024-01-01T00:00:00"
    }


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: str):
    """获取小说信息"""
    # TODO: 实现获取逻辑
    raise HTTPException(status_code=404, detail="Novel not found")


@router.post("/{novel_id}/outline")
async def generate_outline(novel_id: str):
    """生成小说大纲"""
    # TODO: 实现大纲生成
    return {"status": "generating"}


@router.post("/{novel_id}/chapters/{chapter_num}")
async def write_chapter(novel_id: str, chapter_num: int):
    """写作指定章节"""
    # TODO: 实现章节写作
    return {"status": "writing", "chapter": chapter_num}


@router.get("/{novel_id}/chapters")
async def list_chapters(novel_id: str):
    """列出所有章节"""
    # TODO: 实现列表获取
    return {"chapters": []}
