from setuptools import setup, find_packages

setup(
    name="textproc",
    version="0.1",
    author="Egil Moeller",
    author_email="redhog@redhog.org",
    description="",
    long_description="", 
    long_description_content_type="text/markdown",
    url="", 
    license="", 
    packages=find_packages(), 
    install_requires=[
        "aiostream",
        "langchain",
        "langchain-openai",
        "jinja2",
        "jsonpath-ng",
        "pyyaml",
        "aiohttp",
        "html2text",
        "langchain-text-splitters",
    ],
    extras_require={},
    python_requires=">=3.8", 
    classifiers=[],
    entry_points={ 
        'textproc.filter': [
            'templated = textproc.filters.templated:templated',
            'wikipedia = textproc.filters.wikipedia:wikipedia',
            'each = textproc.filters.each:each',
            'chunk = textproc.filters.chunk:chunk',
        ],
    },
    include_package_data=True, 
    project_urls={},
)
