from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    model: str = Field(default="cursor-1")  # Cursor's default model
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=500)

class AppConfig(BaseModel):
    github_token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    cursor_api_key: str = Field(default_factory=lambda: os.getenv("CURSOR_API_KEY", ""))
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    output_format: str = Field(default="console")
    output_file: Optional[str] = Field(default=None)

def validate_config(config: AppConfig) -> bool:
    if not config.github_token:
        raise ValueError("GitHub token is required")
    if not config.cursor_api_key:
        raise ValueError("Cursor API key is required")
    return True 