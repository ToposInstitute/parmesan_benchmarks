"""
Converts the corpora into conll-u format by processing them with spaCy.
"""

import json
import os
import re
import subprocess

from bs4 import BeautifulSoup
from spacy_conll import init_parser
from tqdm import tqdm
from urllib.parse import quote_plus

nlp = init_parser("en_core_web_trf", "spacy", include_headers=True)

PARENTHETICAL = re.compile(r'\(.*\)')

def main():

    print("Converting BCT to conll-u")
    convert_bct()
    print("Converting nLab to conll-u")
    convert_nlab()
    print("Converting TAC to conll-u")
    convert_tac()

def convert_bct():

    with open('corpora/html/bct-corpus/BasicCategoryTheory.html') as infile:
        soup = BeautifulSoup(infile.read(), 'lxml')
        article = soup.find('article')

        for latex in article.find_all(class_="ltx_TOC"):
            latex.extract()

        with open('corpora/conllu/bct.conll', 'w') as outfile:
            doc_id = 0
            sent_id = 0

            title = "Basic Category Theory"
            for section in tqdm(article.find_all(class_=["ltx_para", "ltx_title"])):
                if 'ltx_title' in section['class']:
                    title = section.get_text().strip().replace("\n", " ")
                if 'ltx_para' not in section['class']:
                    continue
                content = section.get_text()
                url = "https://thorsonlinguistics.github.io/bct/#%s" % quote_plus(section['id'])

                if not content.strip():
                    continue

                doc_id += 1

                doc = nlp(content.strip()[:70000])
                outfile.write("# doc_id = %d\n" % doc_id)
                outfile.write("# doc_title = %s\n" % title)
                outfile.write("# doc_url = %s\n" % url)

                sent_id = write_conll(doc, outfile, sent_id)

def convert_nlab():

    doc_id = 0
    sent_id = 0

    with open('corpora/conllu/nlab.conll', 'w') as outfile:
        for (dirpath, dirnames, filenames) in tqdm(os.walk('corpora/html/nlab-content-html/pages')):
            if 'content.html' in filenames and 'name' in filenames:
                content = convert_article(os.path.join(dirpath,
                    'content.html'))
                with open(os.path.join(dirpath, 'name')) as infile:
                    name = infile.read().strip()
            else:
                continue

            title = name
            url = "http://ncatlab.org/nlab/show%s" % quote_plus(name)

            if not content.strip():
                continue

            doc_id += 1
            doc = nlp(content.strip()[:70000])

            outfile.write("# doc_id = %d\n" % doc_id)
            outfile.write("# doc_title = %s\n" % title)
            outfile.write("# doc_url = %s\n" % url)

            sent_id = write_conll(doc, outfile, sent_id)

def convert_tac():

    with open("corpora/json/tac.json") as infile:
        with open("corpora/conllu/tac.conll", 'w') as outfile:
            data = json.load(infile)

            doc_id = 0
            sent_id = 0
            for article in tqdm(data):
                title = article['title']
                url = article['url']
                content = article['abstract']
                keywords = article['keywords']

                if not content:
                    continue

                doc_id += 1

                doc = nlp(content.strip()[:70000])

                outfile.write("# doc_id = %d\n" % doc_id)
                outfile.write("# doc_title = %s\n" % title)
                outfile.write("# doc_url = %s\n" % url)

                sent_id = write_conll(doc, outfile, sent_id)

def write_conll(doc, outfile, sent_id):

    for span in doc._.conll:
        text = ""
        for token in span:
            text += token['FORM']
            if 'SpaceAfter=No' not in token['MISC']:
                text += " "
        text = text.strip()
        if text == "":
            continue
        sent_id += 1
        span_string = re.sub('\s=', ' ', text)
        outfile.write("# sent_id = %d\n" % sent_id)
        outfile.write("# text = %s\n" % span_string)
        for token in span:
            token_conll_str = "\t".join(map(
                map_whitespace,
                token.values(),
            )) + "\n"
            outfile.write(token_conll_str)
        outfile.write("\n")
    outfile.write("\n")

    return sent_id

def convert_article(filename):

    with open(filename) as infile:

        soup = BeautifulSoup(infile.read(), 'lxml')
        content = soup.find(id="Content")
        page_name = content.find(id="pageName")
        revision = content.find(id="revision")

        sidebar = revision.find(class_="rightHandSide")
        if sidebar:
            sidebar.extract()
        toc = revision.find(id="contents")
        if toc:
            toc.extract()
        toc = revision.find(class_="maruku_toc")
        if toc:
            toc.extract()

        for annotation in revision.find_all("annotation"):
            annotation.extract()

        return revision.get_text()

def map_whitespace(label):

    return str(label).replace('\t', '\\t')\
            .replace('\n', '\\n')\
            .replace('\r', '\\r')\
            .replace(' ', '\\s')

if __name__ == "__main__":

    main()
