"""Setup script for backwards compatibility with older pip versions."""

from setuptools import setup, find_packages

setup(
    name="track-selection-engine",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.26.0",
        "pyyaml>=6.0",
        "musicbrainzngs>=0.7.1",
        "mutagen>=1.47.0",
    ],
    entry_points={
        "console_scripts": [
            "track-selector=track_selector.cli:main",
        ],
    },
    python_requires=">=3.10",
)
