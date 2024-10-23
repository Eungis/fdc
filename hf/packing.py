import torch
from transformers import AutoTokenizer

torch.set_printoptions(linewidth=200)

tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Packed Sequence (batched sequence X)

sentence1 = "The cat sat on the mat"
sentence2 = "The dog ate my homework"
sentence3 = "My aunt is a nice teacher"

# Prepare sentences
sentences = [sentence1, sentence2, sentence3]

# Tokenize sentences, Concat each sentence with eos_token_id at the end
tokenized_sentences = tokenizer(sentences, return_attention_mask=False, add_special_tokens=False)["input_ids"]
tokenized_sentences = [t for s in tokenized_sentences for t in s + [tokenizer.eos_token_id]]
print(tokenizer.decode(tokenized_sentences))

# General attention masks
tokenized_sentences = torch.tensor(tokenized_sentences)
print("Size of packed sentence tensor: ", tokenized_sentences.size())

# |Len, Len|
attn_mask = torch.ones(tokenized_sentences.size(0), tokenized_sentences.size(0), dtype=torch.int).tril()
print(attn_mask)


# Generate attention masks specific for packed sequence
def get_attn_mask_for_packed_sequence(tokenized_sentences, tokenizer):
    # get indices of all EOS tokens
    eos_indices = (tokenized_sentences == tokenizer.eos_token_id).nonzero().squeeze()
    # get length of each sequence (including EOS token) from indices
    reps = torch.cat([eos_indices[[0]] + 1, eos_indices[1:] - eos_indices[:-1]])
    repeated_idx = torch.repeat_interleave(eos_indices, reps)

    mask_indices = torch.arange(tokenized_sentences.size(0)).view(-1, 1).expand(-1, tokenized_sentences.size(0))
    mask = torch.ones(tokenized_sentences.size(0), tokenized_sentences.size(0), dtype=torch.bool).tril().expand(-1, -1)
    mask.masked_fill_(mask_indices > repeated_idx, False)
    mask = mask.to(dtype=torch.int)
    return mask


# |Len, Len|
attn_mask = get_attn_mask_for_packed_sequence(tokenized_sentences, tokenizer)
print(attn_mask)


# Generate position ids accordingly
def get_pos_ids_for_packed_sequence(tokenized_sentences, tokenizer):
    org_pos_ids = torch.arange(tokenized_sentences.size(0))
    eos_indices = (tokenized_sentences == tokenizer.eos_token_id).nonzero().squeeze()
    reps = torch.cat([eos_indices[[0]] + 1, eos_indices[1:] - eos_indices[:-1]])
    start_indices = torch.cat([torch.tensor([0]), eos_indices + 1])[:-1]
    pos_ids = org_pos_ids - torch.repeat_interleave(start_indices, reps)
    return pos_ids


pos_ids = get_pos_ids_for_packed_sequence(tokenized_sentences, tokenizer)
print(pos_ids)
