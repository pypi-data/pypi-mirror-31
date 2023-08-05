from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='DB Transfer',
    version="0.3.2",

    description='An easy way to fetch and store data from and store to key-value databases like Redis.',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/arrrlo/python-transfer',
    licence='MIT',

    author='Ivan Arar',
    author_email='ivan.arar@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='database, redis, transfer, migration',

    packages=['transfer'],
    install_requires=[
        'redis~=2.10',
        'ujson~=1.35'
    ],

    entry_points={
        'console_scripts': [
            'transfer=transfer.cli:cli'
        ],
    },

    project_urls={
        'Source': 'https://github.com/arrrlo/python-transfer',
    },
)
