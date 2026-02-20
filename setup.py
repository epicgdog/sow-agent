from setuptools import setup, find_packages

setup(
    name="sow-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.34.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
    ],
    python_requires=">=3.9",
)
