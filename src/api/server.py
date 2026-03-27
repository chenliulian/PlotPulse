"""FastAPI服务"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.models.openai_model import OpenAIModel
from src.pipeline import NovelPipeline


# 全局模型实例
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global model
    # 启动时加载模型
    model = OpenAIModel()
    yield
    # 关闭时清理


app = FastAPI(
    title="PlotPulse API",
    description="AI小说创作服务",
    version="0.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to PlotPulse API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
