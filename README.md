# manga2pdf
## Overview
This Python script is specifically designed to convert manga and comic files, including various formats such as zip, epub, and directories containing image files, to PDF format.

The resulting PDF files are optimized to resemble Japanese manga in terms of page layout and direction. By default, the script uses a "TwoPageRight" page layout that displays two pages side-by-side for a spread view, and a "R2L" (right-to-left) reading direction that is commonly used in Japanese manga.

## Requirement
The script uses the Python libraries **[img2pdf](https://pypi.org/project/img2pdf/)** and **[pikepdf](https://pypi.org/project/pikepdf/)** to do the conversion.
Moreover, it uses **[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)** to read the EPUB files and **[rarfile](https://pypi.org/project/rarfile/)** to read the RAR archive files.

It requires the installation of these packages in order to work properly.

**Note**
- This script can only handle DRM-free fixed-layout EPUB files.
- Please ensure that the image files you input are named in numerical order according to their page sequence. For example, `page_01.jpg`, `page_02.jpg`, `page_03.jpg`, and so on, or `001.jpg`, `002.jpg`, `003.jpg`, and so on. This will ensure that the pages are converted and compiled in the correct order.

## Usage
This script can take input in the form of `zip`, `cbz`, `rar`, `cbr`, `epub` files or directories containing images (`jpg`, `jpeg`, `png`, `gif`, `bmp`) of manga or comic pages.

The program can be executed from the command line with the following options:
- The `input_path` argument represents the path to the input file. To execute the Python script correctly, specify the `input_path` argument as the path to the input file containing manga or comic images in any of the supported formats, such as `zip`, `cbz`, `rar`, `cbr`, `epub`, or a directory containing images in formats such as `jpg`, `jpeg`, `png`, `gif`, or `bmp`.
- The `output_path` argument is the path to the output PDF file. To use the script, simply run the Python script with the path to the input file or directory as the argument. If the `--output` option is not specified, the output file name will be automatically generated based on the name of the input file or directory.
- The `pagelayout` argument is the page layout of the PDF file. The `pagelayout` parameter can take in the following values:
    - `SinglePage` -> Single page display
    - `OneColumn` -> Enable scrolling
    - `TwoPageLeft` -> Spread view
    - `TwoColumnLeft` -> Spread view with scrolling
    - (default) `TwoPageRight` -> Separate Cover, Spread View
    - `TwoColumnRight` -> Separate Cover, Scrolling Spread View
- The `direction` argument is the reading direction of the PDF file. The `direction` parameter can take in the following values:
    - `L2R` -> Left Binding
    - (default) `R2L` -> Right Binding

By default, the page layout is set to `TwoPageRight` and the reading direction to `R2L`, which are suitable for Japanese manga.

The `-j` or `--jpeg` option converts images to JPEG format before including them in the output PDF file, resulting in a smaller file size. Similarly, the `-g` or `--grayscale` option can be used to convert images to grayscale and reduce the size of the resulting PDF file. The program outputs the converted image in the specified format and compresses the PDF file accordingly.

**Note**
- When the original image is already in the JPEG format, using the `-j` or `--jpeg` option will have no effect. Similarly, if the original image is already grayscale, using the `-g` or `--grayscale` option will have no effect. Also, if none of these options are used, the resulting PDF file will not be compressed.

There is a possibility that the script may not be able to handle files in unexpected formats correctly, which may result in errors or unexpected output.

## Installation
### Installing from PyPI
To install the latest version of the package from PyPI, run the following command:
```
$ pip install manga2pdf
```
### Installing directly from the Git repository
To install the package directly from the Git repository, run the following command:
```
$ pip install git+https://github.com/mashu3/manga2pdf.git
```
### Installing by cloning the Git repository
To install the package by cloning the Git repository, follow these steps:
```
$ git clone https://github.com/mashu3/manga2pdf.git
$ cd manga2pdf/
$ pip install .
```
**Note**
- It is recommended to install the package from PyPI, but if you want to try out the latest changes, you can install it from the Git repository.

## Examples
- To convert `my_manga.zip` to `my_manga.pdf` using the default settings:
```
$ manga2pdf my_manga.zip
```
- To convert `my_manga.epub` to `my_manga_spread.pdf` with a spread view and right binding:
```
$ manga2pdf my_manga.epub -o my_manga_spread.pdf
```
- To convert `my_comic.epub` to `my_comic.pdf` with a TwoPage view and left binding:
```
$ manga2pdf my_comic.epub -o my_comic.pdf -p TwoPageLeft -d L2R
```

## Author
[mashu3](https://github.com/mashu3)