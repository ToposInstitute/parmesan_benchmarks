# parmesan_benchmarks

This is the implementation of the experimental procedures and corpus generation
methods described in our 2024 LREC-COLING Paper _Parmesan: Annotated
Mathematical Corpora_. 

Because of conflicting dependencies, we recommend using separate Python virtual
environments for corpus generation and each of the different terminology and
definition extraction models. 

## Corpus Generation

Install the requirements for corpus generation and download the base corpora:

    pip install -r requirements/corpora.txt
    wget -P corpora/json https://raw.githubusercontent.com/ToposInstitute/tac-corpus/main/tac_metadata.json
