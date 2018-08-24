#! /bin/bash

tesseract $1/png/page_$2.png $1/tesseract-txt/page_$2 txt
tesseract $1/png/page_$2.png $1/tesseract/page_$2.html hocr
mv $1/tesseract/page_$2.html.hocr $1/tesseract/page_$2.html
python ocr_annotations.py $1/tesseract/page_$2.html $1/ocr_annotations/page_$2.png
