import transformers
from transformers.data.data_collator import DefaultDataCollator, DataCollatorWithPadding
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
