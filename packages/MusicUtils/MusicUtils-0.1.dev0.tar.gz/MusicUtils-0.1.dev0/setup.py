from setuptools import setup

setup(
    name='MusicUtils',
    version='0.1.dev0',
    packages=['musicutils', ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='Helpful library to download music and metadata from youtube using youtube-dl and by scraping from genius.com.',
    install_requires=[
        'mutagen',
        'eyed3',
        'youtube-dl',
        'lxml',
        'bs4',
        'requests'
    ],
    python_requires='>=3.4',
    classifiers=[
        "Programming Language :: Python :: 3.5"
    ],
    entry_points=dict(console_scripts=[
            'mutils = musicutils.utils:main', ]),
    
)
