"""
Evaluates all terminology generation outputs against the benchmarks.
"""

import json
import os
import spacy

nlp = spacy.load("en_core_web_trf")

def main():

    evaluate_dygiepp()
    #evaluate_textrank()
    #evaluate_spert()
    #evaluate_plmarker()

def evaluate_dygiepp():

    terms = get_dygiepp_terms()

    evaluate_all(terms)

def evaluate_all(predicted):

    for benchmark in ['author_keywords.txt', 'glossary.txt', 'mwe.txt',
            'nlab_titles.txt']:
        for corpus in ['bct']:
        #for corpus in ['bct', 'nlab', 'tac']:
            benchmark_file = os.path.join(os.path.join('benchmarks',
                corpus), benchmark)

            benchmark_terms = set()
            with open(benchmark_file) as infile:
                for line in infile:
                    benchmark_terms.add(line.lower().strip())

            print("EVALUATING BENCHMARK: %s" % benchmark)
            print("AGAINST CORPUS: %s" % corpus)
            evaluate(predicted[corpus], benchmark_terms)
            print("\n\n")

def evaluate(predicted, benchmarks):

    tp = 0.0
    fp = 0.0
    fn = 0.0

    for predicted_term in predicted:
        if predicted_term in benchmarks:
            tp += 1.0
        else:
            fp += 1.0

    for benchmark_term in benchmarks:
        if benchmark_term not in predicted:
            fn += 1.0

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall >= 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    print("Precision: %1.2f" % precision)
    print("Recall: %1.2f" % recall)
    print("F1: %1.2f" % f1)

def get_dygiepp_terms():

    all_terms = {}

    for corpus in ['bct']:
    #for corpus in ['bct', 'tac', 'nlab']:
        corpus_file = os.path.join('predictions/dygiepp', "%s.jsonl" % corpus)

        terms = set()
        with open(corpus_file) as infile:
            for line in infile:
                data = json.loads(line)
                sentences = data['sentences']
                for i in range(len(sentences)):
                    sentence = sentences[i]
                    if data.get('_FAILED_PREDICTION'):
                        continue
                    predicted_ner = data['predicted_ner'][i]
                    for prediction in predicted_ner:
                        start = prediction[0]
                        end = prediction[1] + 1
                        phrase = ' '.join(sentence[start:end])
                        doc = nlp(phrase)
                        lemma_term = ' '.join([token.lemma_ for token in doc])
                        if lemma_term.strip():
                            terms.add(phrase.lower().strip())

        all_terms[corpus] = terms

    return all_terms

if __name__ == "__main__":

    main()
