from setuptools import setup, find_packages

setup(
    name="SEFCNet",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "plotly",
        "pandas",
        "numpy",
        "shap",
        "PyJWT"
    ],
)