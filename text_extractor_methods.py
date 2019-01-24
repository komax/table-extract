#! /usr/bin/env python


import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup
import nltk


def set_up_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', help="input directory containing hocr files")
    parser.add_argument("-o", "--output", help="output file containing the method section")
    return parser


def select_hocr_files(input_dir):
    return sorted(Path(input_dir).glob('*.html'))


stopwords = nltk.corpus.stopwords.words('english')


def stopwords_per_line(words):
    count = 0
    for word in words:
        if word.text in stopwords:
            count += 1
    return count


def build_methods_regex():
    terms = ["Method", "METHOD", "Materials and Methods",
             "MATERIALS AND METHODS", "Materials methods",
             "Material and methods",
             "Study site and methods", "Study Area and Methods",
             "M E T H O D S", "Material and Methods", "STUDY SITE AND METHODS",
             "Materials and Methods", "Study area and methods",
             "Study sites and methods", "MATERIAL AND METHODS",
             "MATERIALS AN D METHODS", "Sample sites and methods"]
    regex = re.compile(r'^([0-9]+.?\s*)?({})'.format("|".join(terms)))
    #print(regex)
    return regex


def build_end_methods_regex():
    terms = ["Discussion", "Conclusion", "Results", "Acknowledgements",
             "Appendix", "Appendices"]
    return re.compile(r'^([0-9]+.?\s*)?({})'.format("|".join(terms)))


def build_literature_heading_regex():
    terms = ["References", "Bibliography", "Literature", "LITERATURE",
             "REFERENCES", "R E F E R E N C E S"]
    return re.compile(r'^([0-9]+.?\s*)?({})'.format("|".join(terms)))


def handle_page(page_path):
    with open(page_path) as hocr:
        page_soup = BeautifulSoup(hocr.read(), 'html.parser')
        regex = build_methods_regex()
        for area in page_soup.find_all("div", "ocr_carea"):
            for i, line in enumerate(area.find_all("span", "ocr_line")):
                words = list(line.find_all("span", "ocrx_word"))
                line_text = " ".join(map(lambda e: e.text, words))
                match = regex.findall(line_text)
                number_stop_words = stopwords_per_line(words)
                print("Number of stop words={} of {} words and ratio={}".format(
                    number_stop_words, len(words), number_stop_words/len(words)))

                if match:
                    print("Match {} at line number {}".format(match, i))
                #print((i, line_text))

            #     for word in line.find_all("span", "ocrx_word"):
            #         pass
            #     text = " ".join(map(lambda e: e.text, list(line.find_all("span", "ocrx_word"))))
            #     print(text)
            #     print("\n\n\n")

                # print("Famous first word: {}".format(line.contents[0]))
                # for word in line.find_all("span", "ocrx_word", id='word_1_561'):
                #     print(word['title'])
                #     print(word['id'])

        #print(page_soup)
        #print(len(page_soup.find_all("span", "ocrx_word")))


def soup_generator(hocr_files):
    for hocr_file in hocr_files:
        with open(hocr_file) as hocr:
            page_soup = BeautifulSoup(hocr.read(), 'html.parser')
            print("handling page={}".format(hocr_file))
            yield page_soup


def detect_start_method_section(hocr_files):
    method_regex = build_methods_regex()

    for page_no, page_soup in enumerate(soup_generator(hocr_files)):
            for area_no, area in enumerate(page_soup.find_all("div", "ocr_carea")):
                for line_no, line in enumerate(area.find_all("span", "ocr_line")):
                    words = list(line.find_all("span", "ocrx_word"))
                    line_text = " ".join(map(lambda e: e.text, words))
                    match = method_regex.findall(line_text)
                    print(line_text)
                    number_stop_words = stopwords_per_line(words)
                    # print(
                    #     "Number of stop words={} of {} words and ratio={}".format(
                    #         number_stop_words, len(words),
                    #         number_stop_words / len(words)))

                    if match:
                        print("Match {} at line number {}".format(match, line_no))
                        return page_no, area_no, line_no

    raise RuntimeError("Cannot find a method section in {}".format(hocr_files[0].parent))


def compose_methods_text(hocr_files, page_no_method_start, area_no_method_start,
                         line_no_method_start):
    method_text = list()

    bib_regex = build_literature_heading_regex()
    method_end_regex = build_end_methods_regex()

    for page_no, page_soup in enumerate(soup_generator(hocr_files)):
        # FIXME Hanlde page_no_method_start differently than others.
        if page_no_method_start <= page_no:
            for area_no, area in enumerate(page_soup.find_all("div", "ocr_carea")):
                if page_no == page_no_method_start and area_no < area_no_method_start:
                    # skip this area because it is not in the methods section.
                    continue
                elif not area['ts:type'] == 'text block':
                    # TODO: less restrictive. Keep anything that is not table or caption or decoration.
                    # skip any area that is not labelled as a text block.
                    continue
                for line_no, line in enumerate(area.find_all("span", "ocr_line")):
                    if page_no == page_no_method_start and area_no_method_start == area_no and line_no < line_no_method_start:
                        # skip this line because it is before the method section starts.
                        continue
                    words = list(line.find_all("span", "ocrx_word"))
                    line_text = " ".join(map(lambda e: e.text, words))
                    # FIXME Find a way to match the end heading which might not be a text block at all.
                    # if method_end_regex.match(line_text) or bib_regex.match(line_text):
                    #     if stopwords_per_line(words) < 2:
                    #         return '\n'.join(method_text)
                    #else:
                    method_text.append(line_text)
    return '\n'.join(method_text)


def main():
    parser = set_up_argparser()
    args = parser.parse_args()
    hocr_files = select_hocr_files(args.inputdir)
    # Sort files by page number.
    hocr_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f.stem))))
    #hocr_files = hocr_files[1:2]

    page_no, area_no_method_start, line_no_method_start = \
        detect_start_method_section(hocr_files)

    method_text = compose_methods_text(hocr_files, page_no,
                                       area_no_method_start,
                                       line_no_method_start)

    print("Detected text in the methods section:")
    print(method_text)


if __name__ == "__main__":
    main()