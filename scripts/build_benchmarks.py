"""
Constructs the benchmark standards for all three corpora. 
"""

import json
import os
import re

from bs4 import BeautifulSoup
from tqdm import tqdm

PARENTHETICAL = re.compile(r'\(.*\)')

def main():

    print("Generating author keywords")
    get_author_keywords()
    print("Generating nLab titles")
    get_nlab_titles()
    print("Generating BCT glossary")
    get_bct_glossary()

def get_author_keywords():

    all_keywords = set()
    with open("corpora/json/tac_metadata.json") as infile:
        with open("benchmarks/author_keywords.txt", 'w') as outfile:
            data = json.load(infile)

            for article in tqdm(data):
                keywords = article['keywords']
                for keyword in keywords:
                    all_keywords.add(keyword.lower())

            for keyword in all_keywords:
                outfile.write(keyword + "\n")

def get_nlab_titles():

    titles = set()

    for (dirpath, dirnames, filenames) in tqdm(os.walk("corpora/html/nlab-content-html/pages")):
        if 'content.html' in filenames and 'name' in filenames:
            with open(os.path.join(dirpath, 'name')) as infile:
                titles.add(infile.read().strip().lower())

    with open("benchmarks/nlab_titles.txt", 'w') as outfile:
        for title in titles:
            if title.strip():
                outfile.write(title.strip() + '\n')

def get_bct_glossary():

    glossary = set()
    definitions = []

    with open("corpora/html/bct-corpus/BasicCategoryTheory.html") as infile:

        soup = BeautifulSoup(infile.read(), 'lxml')
        article = soup.find("article")

        for latex in article.find_all(class_="ltx_TOC"):
            latex.extract()

        for gloss_item in article.find_all(
                lambda x: "ltx_indexphrase" in x.get('class', []) and
                    len(x.find_parents(class_="ltx_indexentry")) <= 1
                ):
            glossary.add(gloss_item.get_text().strip().lower())

        for definition in article.find_all(
                lambda x: "ltx_theorem_defn" in x.get('class', [])
                ):
            paragraph = definition.find(class_="ltx_para")
            text = paragraph.get_text().strip()
            headwords = [headword.get_text().strip() for headword in
                    paragraph.find_all(class_="ltx_font_bold")]

            for headword in headwords:
                definitions.append({
                    "headword": headword,
                    "definition": text,
                })

        with open("benchmarks/glossary.txt", 'w') as outfile:
            for item in glossary:
                normalized = item.replace('’', "'")
                split = normalized.split(',')
                if len(split) == 2:
                    normalized = '%s %s' % (split[1].strip(), split[0])
                parenthetical = PARENTHETICAL.search(normalized)
                if parenthetical is not None:
                    second_item = parenthetical.group(0)
                    normalized = PARENTHETICAL.sub('', normalized)
                    outfile.write(second_item.replace('(', '').replace(')', '') + '\n')
                outfile.write(normalized + '\n')

        with open('benchmarks/definitions.json', 'w') as outfile:
            json.dump(definitions, outfile)

if __name__ == "__main__":

    main()
