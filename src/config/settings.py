from pydantic import BaseModel, Field
import os
from typing import Optional

class LLMConfig(BaseModel):
    """Configuration for the LLM model."""
    model_path: str = Field(..., description="Path to the GGUF model file")
    context_window: int = Field(default=4096, description="Context window size")
    max_tokens: int = Field(default=512, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    n_threads: int = Field(default=4, description="Number of threads to use")
    use_metal: bool = Field(default=True, description="Use Metal acceleration for Apple Silicon")
    n_gpu_layers: int = Field(default=1, description="Number of layers to offload to GPU")

class AppConfig(BaseModel):
    """Main application configuration."""
    github_token: str = Field(..., description="GitHub Personal Access Token")
    llm_config: LLMConfig = Field(..., description="LLM configuration")
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Path to log file")

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.github_token:
            raise ValueError("GitHub token is required. Please set GITHUB_TOKEN in .env file.") 