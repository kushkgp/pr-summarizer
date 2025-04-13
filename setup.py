from setuptools import setup, find_packages

setup(
    name="pr-summarizer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "llama-cpp-python>=0.2.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pr-summarizer=pr_summarizer.main:main",
            "download-model=download_model:main",
        ],
    },
) 