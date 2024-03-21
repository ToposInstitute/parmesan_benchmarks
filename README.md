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

The MWE-based benchmarks are constructed using the MWEToolkit, which must first
be installed:

    git clone git@gitlab.com:mwetoolkit/mwetoolkit3.git
    cd mwetoolkit3
    make
    cd ..

Then, run the toolkit on each of the three corpora:

    python mwetoolkit3/bin/candidates.py -p patterns/np.xml --to PlainCandidates corpora/conllu/bct.conll > benchmarks/bct/mwe.txt
    python mwetoolkit3/bin/candidates.py -p patterns/np.xml --to PlainCandidates corpora/conllu/tac.conll > benchmarks/tac/mwe.txt
    python mwetoolkit3/bin/candidates.py -p patterns/np.xml --to PlainCandidates corpora/conllu/nlab.conll > benchmarks/nlab/mwe.txt

Finally, we need to construct extractive versions of the base benchmarks:

    python scripts/build_extractive_benchmarks.py

Some of the models require additional corpus processing.

### DyGIE++

To convert the corpora into an appropriate format for DyGIE++, run the
following script:

    python scripts/build_dygiepp.py

## Terminology Generation

### DyGIE++

Note that you will probably need to switch to a new virtual environment for
DyGIE++, since it is incompatible dependencies. First, install DyGIE++ and its
dependencies as well as the pretrained model:

    git clone https://github.com/dwadden/dygiepp.git
    pip install -r requirements/dygiepp.txt
    mkdir dygiepp/pretrained
    wget -P dygiepp/pretrained https://s3-us-west-2.amazonaws.com/ai2-s2-research/dygiepp/master/scierc.tar.gz

To generate the analysis for each corpus, run:

    cd dygiepp
    allennlp predict pretrained/scierc.tar.gz \
        ../corpora/dygiepp/bct.jsonl \
        --predictor dygie \
        --include-package dygie \
        --use-dataset-reader \
        --output-file ../predictions/dygiepp/bct.jsonl \
        --cuda-device 0 \
        --silent

### Evaluation

To run evaluations on all of the predicted values for all corpora and
terminology generation models, run:

    python scripts/evaluate_terminology.py
