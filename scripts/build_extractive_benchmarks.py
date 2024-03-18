import os
import re
import spacy

from conllu import parse_incr
from tqdm import tqdm

nlp = spacy.load("en_core_web_trf")

def main():

    for corpus in ['corpora/conllu/bct.conll', 'corpora/conllu/nlab.conll',
            'corpora/conllu/tac.conll']:
        for benchmark in ['benchmarks/author_keywords.txt',
                'benchmarks/glossary.txt', 'benchmarks/nlab_titles.txt']:
            extract(corpus, benchmark)

def extract(corpus, benchmark):

    corpus_name = os.path.basename(os.path.splitext(corpus)[0])
    benchmark_name = os.path.basename(benchmark)

    print("Parsing %s benchmark for %s" % (benchmark_name, corpus_name))

    with open(benchmark) as benchmark_file:
        benchmark_terms = set()
        for line in tqdm(benchmark_file):
            base_term = line.strip().lower().replace('_', ' ')
            doc = nlp(base_term)
            lemma_term = ' '.join([token.lemma_ for token in doc])
            if lemma_term.strip():
                benchmark_terms.add(lemma_term.strip())
        with open(corpus) as corpus_file:
            extractive_terms = set()

            for sentence in tqdm(parse_incr(corpus_file)):
                text = ' '.join((token['lemma'] for token in sentence))
                for benchmark_term in benchmark_terms:
                    if re.search(r'\b' + re.escape(benchmark_term) + r'\b',
                            text):
                        extractive_terms.add(benchmark_term)

            with open('benchmarks/%s/%s' % (corpus_name, benchmark_name), 'w') as outfile:
                for term in extractive_terms:
                    outfile.write("%s\n" % term)

if __name__ == "__main__":

    main()
