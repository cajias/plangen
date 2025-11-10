from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plangen",
    version="0.1.0",
    description="A multi-agent framework for generating planning and reasoning trajectories with LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Carlos Cajias",
    author_email="cajias@example.com",
    maintainer="PlanGEN Team",
    maintainer_email="plangen@example.com",
    url="https://github.com/cajias/plangen",
    project_urls={
        "Bug Tracker": "https://github.com/cajias/plangen/issues",
        "Changelog": "https://github.com/cajias/plangen/releases",
        "Documentation": "https://github.com/cajias/plangen/tree/main/docs",
        "Source Code": "https://github.com/cajias/plangen",
    },
    license="MIT",
    keywords=["llm", "planning", "agents", "multi-agent", "generative-ai"],
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "pydantic>=2.6.1",
        "tenacity>=8.2.3",
        "numpy>=1.20.0",
        "langgraph>=0.1.11",
        "boto3>=1.34.0",
        "jinja2>=3.1.2",
        "networkx>=3.1",
        "matplotlib>=3.7.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=24.1.1",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.5",
        ],
    },
    python_requires=">=3.9,<3.13",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
