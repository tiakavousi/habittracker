from setuptools import setup, find_packages

setup(
    name="habit_tracker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pytest>=7.4.0",
    ],
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
