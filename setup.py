from setuptools import setup, find_packages


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='interpals-api',
    version="2.3.0",
    author='Alexander Khlebushchev',
    description="Unofficial Python API for Interpals.net.",
    url="https://github.com/fomalhaut88/interpals-api",
    project_urls={
        "Homepage": "https://pypi.org/project/interpals-api/",
        "Documentation": "https://fomalhaut88.github.io/interpals-api/",
        "Source": "https://github.com/fomalhaut88/interpals-api",
        "Issues": "https://github.com/fomalhaut88/interpals-api/issues",
    },
    packages=find_packages(),
    license="MIT",
    zip_safe=False,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8',
        'requests>=2.31',
        'lxml>=4.9',
        'beautifulsoup4>=4.12',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)
