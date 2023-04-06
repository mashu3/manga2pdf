from setuptools import setup, find_packages

VERSION = "0.0.3"

INSTALL_REQUIRES = (
    "img2pdf",
    "Pillow",
    "pikepdf",
    "rarfile",
    "beautifulsoup4"
)
CLASSIFIERS=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11'
]

setup(
    name="manga2pdf",
    version=VERSION,
    author="mashu3",
    description="Convert manga/comic files(zip, epub, etc.) or directory containing image files (jpg, png, etc.) to PDF.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="manga comic pdf converter",
    url="https://github.com/mashu3/manga2pdf",
    license='MIT',
    package_dir={"": "src"},
    py_modules=["manga2pdf"],
    packages = find_packages("src"),
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "manga2pdf=manga2pdf:main",
        ]
    }
)