"""
Converts the conll-u corpora into DyGIE++'s JSON input format.
"""

import json
import os
import uuid

from conllu import parse_incr
from tqdm import tqdm

def main():

    for corpus in ['corpora/conllu/bct.conll']:
        convert(corpus)

def convert(corpus):

    corpus_name = os.path.splitext(os.path.basename(corpus))[0]
    data = []
    with open(corpus) as corpus_file:
        with open(os.path.join('corpora/spert', corpus_name + '.json'), 'w') as outfile:
            current_document = None
            for sentence in tqdm(parse_incr(corpus_file)):
                if len(sentence) > 180:
                    continue
                if 'ROOT' not in [token['deprel'] for token in sentence]:
                    continue
                data.append({
                    'tokens': [token['form'] for token in sentence],
                    'pos_tags': [normalize_xpos(token['xpos']) for token in sentence],
                    'dep_label': [token['deprel'] for token in sentence],
                    'verb_indicator': [(1 if token['upos'] == 'VERB' else 0) for
                        token in sentence],
                    'dep_head': [token['head'] for token in sentence],
                    'entities': [],
                    'relations': [],
                    'orig_id': str(uuid.uuid4()),
                })

            json.dump(data, outfile)

def normalize_xpos(xpos):

    if xpos in ['_SP']:
        return 'XX'
    else:
        return xpos

if __name__ == "__main__":

    main()
