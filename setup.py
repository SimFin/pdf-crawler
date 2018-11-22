from setuptools import setup

setup(
    name='pdf-crawler',
    version='0.1',
    install_requires=[
        'beautifulsoup4',
        'click',
        'fake_useragent',
        'requests',
        'selenium',
        'requests_html'
    ],
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
            'pytest-flakes',
            'pytest-pep8',
        ],
    },
    entry_points={
        'console_scripts': [
            'pdf-crawler = crawler:crawl',
        ],
    },
)
