from setuptools import setup, find_packages

setup(
    name="novaengine",
    version="1.0.0",
    author="Raúl Salas Sahuquillo",
    author_email="raulsalassahuquillo.dev@gmail.com",
    description="Headless quantitative trading engine, real-time market data pipelines, and multi-jurisdiction fiscal auditing.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/raulsalas/NovaEngine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.0",
        "typing-extensions>=4.8.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "novaengine=novaengine.cli:main",
        ],
    },
)
