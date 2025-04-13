from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv

class LLMConfig(BaseModel):
    """Configuration for the LLM model."""
    model_path: str = Field(default="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.95)
    repeat_penalty: float = Field(default=1.1)
    context_window: int = Field(default=4096)

class AppConfig(BaseModel):
    """Application configuration."""
    github_token: str
    llm_config: LLMConfig = Field(default_factory=LLMConfig)

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        load_dotenv()
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
        return cls(github_token=github_token) 