from setuptools import setup, find_packages

setup(
    name="web_search",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "PyMuPDF",
        "selenium",
    ],
    author="Nishio",
    description="A tool to perform DuckDuckGo search and extract contents.",
    url="https://github.com/west0714/web_search",
    python_requires='>=3.7',
)
