from setuptools import setup, find_packages

setup(
    name="plangen",
    version="0.1.0",
    description="A multi-agent framework for generating planning and reasoning trajectories",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "pydantic>=2.6.1",
        "tenacity>=8.2.3",
        "numpy>=1.26.3",
        "langgraph>=0.1.11",
        "boto3>=1.34.0",
        "jinja2>=3.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "mypy>=1.8.0",
            "pytest-cov>=4.1.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)