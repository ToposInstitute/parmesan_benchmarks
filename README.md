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

### Textrank

The textrank dependencies are installed with the corpus dependencies above, as
there are no conflicting dependencies at this time. To generate the
terminology, run:

    python scripts/build_textrank.py

### SpERT.PL

Again, a separate virtual environment is recommended. Download the repository and extract the code:

    git clone https://github.com/dksanyal/SpERT.PL
    unzip SpERT.PL/CodeFinal.zip -d SpERT.PL/

Download the pretrained models:

    wget -P SpERT.PL/CodeFinal/InputsAndOutputs/pretrained/ https://s3-us-west-2.amazonaws.com/ai2-s2-research/scibert/huggingface_pytorch/scibert_scivocab_cased.tar
    tar xvf SpERT.PL/CodeFinal/InputsAndOutputs/pretrained/scibert_scivocab/cased/scibert_scivocab_cased.tar

Install the required dependencies:

    pip install -r requirements/spert.txt

Train the model:

    python scripts/train_spert.py

Run the model to produce predictions (ignore the output scores, we are only
generating examples, not evaluating them yet):

    python scripts/run_spert.py

It may be necessary to change the names of the directories in these scripts to
match the latest run. 

Copy the predictions to the appropriate directory (you will need to change the
directory name to match yours):

    cp SpERT.PL/CodeFinal/InputsAndOutputs/data/log/\'scierc_eval\'/DIRNAME/examples_entities_sorted_test_epoch_0.html predictions/spert/bct.html

### PL-Marker

Again, a separate virtual environment is recommended. Download the repository
and install the dependencies:

    git clone https://github.com/thunlp/PL-Marker
    pip install -r PL-Marker/requirements.txt
    pip install -e PL-Marker/transformers

Download the pretrained models from [here](https://drive.google.com/drive/folders/1_ccNEm9LlqegoGXl69PJEbSW16Qvx7X7) and place them in `PL-Marker/sciner-scibert`.

Also download the necessary BERT models.

    wget -P PL-Marker/bert_models/scibert_scivocab_uncased https://huggingface.co/allenai/scibert_scivocab_uncased/resolve/main/pytorch_model.bin
    wget -P PL-Marker/bert_models/scibert_scivocab_uncased https://huggingface.co/allenai/scibert_scivocab_uncased/resolve/main/vocab.txt
    wget -P PL-Marker/bert_models/scibert_scivocab_uncased https://huggingface.co/allenai/scibert_scivocab_uncased/resolve/main/config.json

PL-Marker uses the same data format as DyGIE++, so we can reuse the same
corpora from before. To run PL-Marker on a corpus, run:

    python scripts/run_acener.py --model_type bertspanmarker \
        --model_name_or_path  PL-Marker/bert_models/scibert_scivocab_uncased --do_lower_case \
        --data_dir corpora/dygiepp/ \
        --per_gpu_eval_batch_size 16 \
        --max_seq_length 512 --max_pair_length 256 --max_mention_ori_length 8 \
        --do_eval \
        --fp16 --seed 42 --onedropout --lminit \
        --test_file bct.jsonl \
        --output_dir predictions/plmarker/bct --overwrite_output_dir --output_results

### Evaluation

To run evaluations on all of the predicted values for all corpora and
terminology generation models, run:

    python scripts/evaluate_terminology.py
