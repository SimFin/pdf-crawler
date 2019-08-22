from setuptools import setup

setup(
    name='pdf-crawler',
    version='0.1',
    install_requires=[
        'beautifulsoup4',
        'click',
        'requests',
        'selenium',
        'requests_html',
        'psutil'
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
