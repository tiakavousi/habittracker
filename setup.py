from setuptools import find_packages, setup

setup(
    name="habit_tracker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pytest>=7.4.0",
        "PyYAML>=6.0.1",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "habit-tracker=habit_tracker.cli:main",
        ],
    },
    author="Tia Kavousi",
    author_email="tayebekavousi68@gmail.com",
    description="A habit tracking application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
