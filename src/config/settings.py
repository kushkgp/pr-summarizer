from pydantic import BaseModel, Field
import os
from typing import Optional

class LLMConfig(BaseModel):
    """Configuration for LLM model."""
    model_path: str = Field(default="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.95)
    repeat_penalty: float = Field(default=1.1)

class AppConfig(BaseModel):
    """Main application configuration."""
    github_token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    llm_config: LLMConfig = Field(default_factory=LLMConfig)

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.github_token:
            raise ValueError("GitHub token is required. Please set GITHUB_TOKEN in .env file.") 