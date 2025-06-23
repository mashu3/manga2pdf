from setuptools import setup, find_packages

VERSION = "0.2.6"

install_requires = [
    "lxml",
    "numpy",
    "img2pdf",
    "Pillow",
    "pikepdf",
    "rarfile",
    "i18nice[YAML]"
]

extras_require = {
    'windows': ["win32_setctime"]
}

CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13'
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
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "manga2pdf": ["locales/*.yml"]
    },
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "manga2pdf=manga2pdf.manga2pdf:main",
        ]
    }
)