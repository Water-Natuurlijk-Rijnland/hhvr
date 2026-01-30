from setuptools import setup, find_packages

setup(
    name="peilbeheer-hhvr",
    version="2.0.0",
    description="Water level management tools for Hoogheemraadschap van Rijnland",
    author="Hoogheemraadschap van Rijnland",
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)
