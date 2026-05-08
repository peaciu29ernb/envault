"""Package setup for envault."""

from setuptools import setup, find_packages


setup(
    name="envault",
    version="0.1.0",
    description="Lightweight utility to encrypt and manage per-project .env files with key rotation support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="envault contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "cryptography>=41.0",
        "click>=8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "envault=envault.cli:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
    project_urls={
        "Source": "https://github.com/example/envault",
        "Bug Tracker": "https://github.com/example/envault/issues",
    },
)
