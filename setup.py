from setuptools import setup, find_packages


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='interpals-api',
    version="2.2.0",
    author='Alexander Khlebushchev',
    packages=find_packages(),
    license="MIT",
    zip_safe=False,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    data_files=[],
    install_requires=[
        'aiohttp>=3.8',
        'PyYAML>=6.0',
        'requests>=2.31',
        'lxml>=4.9',
        'beautifulsoup4>=4.12',
    ],
)
