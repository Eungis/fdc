import transformers
import random
from datasets import load_dataset
from transformers.data.data_collator import (
    DefaultDataCollator,
    DataCollatorWithPadding,
    DataCollatorForTokenClassification
)
from transformers import AutoTokenizer
from torch.utils.data import DataLoader, Dataset

transformers.logging.set_verbosity(transformers.logging.WARNING)

print("========= DefaultDataCollator =========")

# Prepare sample data
sentences = [
    "Hello, how are you?",
    "I am learning to use the transformers library.",
    "This is an example for DefaultDataCollator.",
]

tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token_id = tokenizer.eos_token_id

# Tokenize sentences and make as Dataset
tokenized_sentences = tokenizer(sentences, truncation=False, padding=True, add_special_tokens=False)
dataset = [
    {"input_ids": input_ids, "attention_mask": attention_mask}
    for input_ids, attention_mask in zip(tokenized_sentences["input_ids"], tokenized_sentences["attention_mask"])
]

# Initialize the DefaultDataCollator
data_collator = DefaultDataCollator()
loader = DataLoader(dataset=dataset, batch_size=2, collate_fn=data_collator)
for batch in loader:
    print(batch)

print("========= DataCollatorWithPadding =========")

sentences = [
    "Hello, how are you?",
    "I am learning to use the transformers library.",
    "This is an example for DefaultDataCollator.",
]
labels = [1, 2, 3]
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token_id = tokenizer.eos_token_id


class SimpleDataset(Dataset):
    def __init__(self, input_ids, attention_mask, labels):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.labels = labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        # PreTrainedTokenizerBase - model_input_names: ["input_ids", "token_type_ids", "attention_mask"]
        return {"input_ids": self.input_ids[idx], "attention_mask": self.attention_mask[idx], "label": self.labels[idx]}


# Tokenize Sentences
# Here to set padding as False to simulate the DataCollatorWithPadding.
# return_tensors cannot be "pt" because the lengths are different.
tokenized_sentences = tokenizer(sentences, padding=False, return_tensors="np", add_special_tokens=False)

# 1. Way to make dataset as dictionary directly
# dataset = [
#     {"input_ids": input_ids, "attention_mask": attention_mask, "label": label}
#     for input_ids, attention_mask, label in zip(
#        tokenized_sentences["input_ids"], tokenized_sentences["attention_mask"], labels
#     )
# ]

# 2. Way to make dataset as torch.utils.data.Dataset
input_ids = [input_ids for input_ids in tokenized_sentences["input_ids"]]
attention_mask = [attention_mask for attention_mask in tokenized_sentences["attention_mask"]]
dataset = SimpleDataset(input_ids, attention_mask, labels)


# It internally do things as follow:
# 1. Get batch according to the batch_size from dataset. ex. dataset[:2]
# 2. use `tokenizer.pad(dataset[:2])` to pad the dataset
# 3. If "label" keyword in dataset, change it to "labels" and return the padded result.
data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer, padding=True, return_tensors="pt"  # bool, Literal["longest", "max_length", "do_not_pad"]
)
loader = DataLoader(dataset, batch_size=2, collate_fn=data_collator)
for batch in loader:
    print(batch)

print("========= DataCollatorForTokenClassification =========")  

# Use NER example
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
raw_datasets = load_dataset("conll2003")
print("NER tags: ", raw_datasets["test"].features["ner_tags"].feature.names)
print("Sample tokens: ", raw_datasets["test"][2]["tokens"])
print("Sample tags: ", raw_datasets["test"][2]["ner_tags"])

# Get sample dataset
sample_num = random.randint(0, raw_datasets["test"].num_rows)
words = raw_datasets["test"][sample_num]["tokens"]
labels = raw_datasets["test"][sample_num]["ner_tags"]
label_names = raw_datasets["test"].features["ner_tags"].feature.names

# Align tokens with label
line1, line2 = "", ""
for word, label in zip(words, labels):
    full_label = label_names[label]
    max_length = max(len(word), len(full_label))
    line1 += word + " " * (max_length - len(word) + 1)
    line2 += full_label + " " * (max_length - len(full_label) + 1)
    
print(line1)
print(line2)

# Prepare datasets
tokenized_input = tokenizer(
    words,
    is_split_into_words=True, # !important in NER cases
    return_offsets_mapping=True,
    add_special_tokens=True
)
print(tokenized_input.tokens(batch_index=0))

def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    for word_id in word_ids:
        if word_id is None: # special tokens output as None in word_ids()
            new_labels.append(-100)
        else:
            label = -100 if word_id is None else labels[word_id]
            new_labels.append(label)
        # No prob if unifying B-XXX with I-XXX label
    return new_labels

# if tokenizer.is_fast is True, the function below is useful when mapping the word to token.
# https://huggingface.co/docs/transformers/index#supported-frameworks
if tokenizer.is_fast:
    word_ids = tokenized_input.word_ids(batch_index=0)
    print("words: ", words)
    print("labels: ", labels)
    alinged_labels = align_labels_with_tokens(labels, word_ids)
    print("word_ids: ", word_ids)
    print("aligned: ", [label_names[label_id] if label_id >= 0 else None for label_id in alinged_labels])


collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    return_tensors="pt",
    label_pad_token_id=-100
)

dataset = raw_datasets["test"][:10]

# Prepare inputs
tokenized_inputs = tokenizer(
    dataset["tokens"],
    is_split_into_words=True,
    return_offsets_mapping=True,
    add_special_tokens=True,
    return_tensors="pt",
    padding=True
)

# Prepare labels
word_ids = [tokenized_inputs.word_ids(batch_index=i) for i in range(len(tokenized_inputs))]
labels = [ner_tag for ner_tag in dataset["ner_tags"]]
aligned_labels = [align_labels_with_tokens(label, word_id) for word_id, label in zip(word_ids, labels)]

assert all(
    [
        len(input_id) == len(label)
        for input_id, label in zip(tokenized_inputs["input_ids"], aligned_labels)
    ]
)

dataset = [
    {
        "input_ids": input_ids,
        "labels": labels,
        "attention_mask": attention_mask,
    } for input_ids, attention_mask, labels in zip(
        tokenized_inputs["input_ids"],
        tokenized_inputs["attention_mask"],
        aligned_labels
    )
]
loader = DataLoader(
    dataset=dataset,
    batch_size=2,
    shuffle=True,
    collate_fn=collator
)

batch = next(iter(loader))
