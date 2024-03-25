# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:04:56 2021

@author: DS
"""

import sys

sys.path.append('SpERT.PL/CodeFinal/SynSpERT')


import Runner
BASE_DIR="SpERT.PL/CodeFinal/InputsAndOutputs/"

BERT_PATH = BASE_DIR+"pretrained/scibert_scivocab_cased"   ### For SciERC
#BERT_PATH = BASE_DIR+"pretrained/biobert_base_cased"      ### For ADE
TOKENIZER_PATH= BERT_PATH
MODEL_TYPE="syn_spert"
CONFIG_PATH= BASE_DIR + "configs/config.json"

LOG_PATH=  BASE_DIR + "data/log/"
SAVE_PATH= BASE_DIR + "data/save/"
CACHE_PATH= BASE_DIR + "data/cache/"


############ SCIERC ###########
TRAIN_PATH= BASE_DIR + "data/datasets/scierc/scierc_train_dev_aug.json"
VALID_PATH= BASE_DIR + "data/datasets/scierc/scierc_test_aug.json"  #same as test path (we do not tune hyperparams)
TEST_PATH=  BASE_DIR + "data/datasets/scierc/scierc_test_aug.json"
TYPES_PATH= BASE_DIR + "data/datasets/scierc/scierc_types.json"


############# ADE ############## 
'''
TRAIN_PATH= BASE_DIR + "data/datasets/ade/ade_split_2_train_aug.json"
VALID_PATH= BASE_DIR + "data/datasets/ade/ade_split_2_test_aug.json"
TYPES_PATH= BASE_DIR + "data/datasets/ade/ade_types.json"
TEST_PATH= VALID_PATH
'''

#==============================================================
TRAIN = True #False ##for evaluation
#==============================================================
MODEL_PATH = SAVE_PATH + "'scierc_train'/2021-07-15_01-46-42.294760/final_model/"

#==============================================================
SEED=656 
USE_POS='--use_pos' 
USE_ENTITY_CLF='logits'     #Choices: none, logits, softmax, onehot

if __name__ == "__main__": 
    if TRAIN==True:  
      input_args_list = f"train --model_type {MODEL_TYPE} --label 'scierc_train' \
        --model_path  {BERT_PATH} --tokenizer_path  {BERT_PATH} \
        --train_path  {TRAIN_PATH} --valid_path {VALID_PATH} \
        --types_path {TYPES_PATH} --cache_path  {CACHE_PATH} \
        --size_embedding 25 --train_batch_size 10 \
         {USE_POS} --pos_embedding 25 \
        --use_entity_clf {USE_ENTITY_CLF} \
        --eval_batch_size 2 --epochs 2 --lr 5e-5 --lr_warmup 0.1 \
        --weight_decay 0.01 --max_grad_norm 1.0 --prop_drop 0.1 \
        --neg_entity_count 100 --neg_relation_count 100 \
        --max_span_size 10 --rel_filter_threshold 0.4 --max_pairs 1000 \
        --sampling_processes 4 --sampling_limit 100  \
        --store_predictions True --store_examples True \
        --log_path  {LOG_PATH} --save_path {SAVE_PATH} \
        --max_seq_length 512 --config_path  {CONFIG_PATH} \
        --gradient_accumulation_steps 1 --wordpiece_aligned_dep_graph --seed {SEED} \
        --final_eval"

    else:
        input_args_list = f"eval --model_type {MODEL_TYPE} --label 'scierc_eval' \
          --model_path  {MODEL_PATH} --tokenizer_path {MODEL_PATH} \
          --dataset_path {TEST_PATH}  \
          --types_path  {TYPES_PATH}  --cache_path {CACHE_PATH} \
          --size_embedding 25 \
           {USE_POS} --pos_embedding 25 \
          --use_entity_clf {USE_ENTITY_CLF} \
          --eval_batch_size 1  --lr 5e-5 --lr_warmup 0.1 \
          --weight_decay 0.01 --max_grad_norm 1.0 --prop_drop 0.1 \
          --max_span_size 10 --rel_filter_threshold 0.4 --max_pairs 1000 \
          --sampling_processes 4 --sampling_limit 100 \
          --store_predictions True --store_examples True \
          --log_path {LOG_PATH} --save_path {SAVE_PATH} \
          --max_seq_length 512 --config_path {CONFIG_PATH} \
          --gradient_accumulation_steps 1  --wordpiece_aligned_dep_graph --seed {SEED}" #\
#          --no_overlapping"
        
    print("*** Commandline: ", input_args_list)

    input_args_list = input_args_list.split() 
    #print(input_args_list)
    r = Runner.Runner()
    r.run(input_args_list)

