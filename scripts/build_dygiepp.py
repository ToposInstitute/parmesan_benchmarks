"""
Converts the conll-u corpora into DyGIE++'s JSON input format.
"""

import json
import os

from conllu import parse_incr
from tqdm import tqdm

def main():

    for corpus in ['corpora/conllu/bct.conll']:
        convert(corpus)

class Document:

    def __init__(self, title, url):

        self.title = title
        self.url = url
        self.sentences = []

def convert(corpus):

    corpus_name = os.path.splitext(os.path.basename(corpus))[0]

    with open(corpus) as corpus_file:
        with open(os.path.join('corpora/dygiepp', corpus_name + '.jsonl'), 'w') as outfile:
            current_document = None
            for sentence in tqdm(parse_incr(corpus_file)):
                if 'doc_id' in sentence.metadata:
                    if current_document:
                        json_string = json.dumps({
                            'doc_key': current_document.url,
                            'dataset': 'scierc',
                            'sentences': current_document.sentences,
                            'ner': [[] for i in range(len(current_document.sentences))],
                            'relations': [[] for i in range(len(current_document.sentences))],
                        })
                        outfile.write(json_string + "\n")
                    current_document = Document(
                        title=sentence.metadata.get('doc_title', "Untitled"),
                        url=sentence.metadata['doc_url'],
                    )

                if current_document is None:
                    continue

                current_document.sentences.append([token['form'] for token in
                    sentence])

            if current_document:
                json_string = json.dumps({
                    'doc_key': current_document.url,
                    'dataset': 'scierc',
                    'sentences': current_document.sentences,
                    'ner': [[] for i in range(len(current_document.sentences))],
                    'relations': [[] for i in range(len(current_document.sentences))],
                })
                outfile.write(json_string + "\n")

if __name__ == "__main__":

    main()
