from setuptools import setup, find_packages

setup(
    name="delta_neutral_strategy",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "kiteconnect>=4.1.0",
        "python-dotenv>=0.19.0",
        "logging>=0.5.1",
        "pytest>=6.2.5",
    ],
    author="Vikas",
    description="A delta-neutral options trading strategy implementation",
    keywords="trading, options, delta-neutral, algorithmic-trading",
    python_requires=">=3.8",
)