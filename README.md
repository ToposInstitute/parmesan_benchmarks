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
    git clone https://github.com/ncatlab/nlab-content-html.git corpora/html/nlab-content-html
    git clone https://github.com/ToposInstitute/CT-corpus corpora/latex/bct-corpus

The BCT corpus needs to be converted from LaTeX into HTML. This is done with
[latexml](https://math.nist.gov/~BMiller/LaTeXML/), which must be installed on
your system following the directions on the website.

    latexmlpost --dest=corpora/html/bct-corpus/BasicCategoryTheory.html corpora/latex/bct-corpus/latex/BasicCategoryTheory.xml

Some errors and warnings will appear, but these can generally be ignored.

Finally,  build the conll-u corpora from the original sources:

    python scripts/build_conllu.py

## Benchmark Generation

Most benchmarks are generated from the corpora and associated metadata. Most
benchmarks are generated automatically with the following command:

    python scripts/build_benchmarks.py
