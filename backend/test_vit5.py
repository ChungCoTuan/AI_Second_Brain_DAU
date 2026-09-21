from transformers import AutoTokenizer
import json
import os
import shutil
from huggingface_hub import hf_hub_download

# Download tokenizer_config.json
config_path = hf_hub_download(repo_id='VietAI/vit5-base-vietnews-summarization', filename='tokenizer_config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Delete 'vocab' from config to prevent the Unigram bug
if 'vocab' in config:
    print("Found 'vocab' dict! Deleting it to avoid transformers 4.40+ bug.")
    del config['vocab']

# Save patched config to a local dir
os.makedirs('patched_tokenizer', exist_ok=True)
with open('patched_tokenizer/tokenizer_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f)

# Download spiece.model
spiece_path = hf_hub_download(repo_id='VietAI/vit5-base-vietnews-summarization', filename='spiece.model')
shutil.copy(spiece_path, 'patched_tokenizer/spiece.model')

# Load tokenizer from patched dir
t = AutoTokenizer.from_pretrained('patched_tokenizer', use_fast=False)
print('Loaded successfully! Vocab size:', len(t))
