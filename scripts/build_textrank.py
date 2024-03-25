"""
Generate terminology using the textrank algorithm.
"""

from conllu import parse_incr
from tqdm import tqdm

import pytextrank
import spacy

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('textrank')

def main():

    for corpus in ['bct', 'tac', 'nlab']:
        keywords = set()
        with open('corpora/conllu/%s.conll' % corpus) as infile:
            with open('predictions/textrank/%s.txt' % corpus, 'w') as outfile:
                for sentence in tqdm(parse_incr(infile)):
                    text = ' '.join((token['form'] for token in sentence if token.strip()))
                    doc = nlp(text)
                    for phrase in doc._.phrases:
                        lemma_term = ' '.join([token.lemma_ for token in [span for span in phrase.chunks]])
                        if lemma_term.strip():
                            keywords.add(lemma_term.lower().strip())

                for keyword in keywords:
                    outfile.write(keyword + '\n')

if __name__ == "__main__":

    main()
