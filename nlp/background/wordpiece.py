# wordpiece algorithm
# score = freq_pair / (freq_first * freq_second)
import logging
from typing import List
from transformers import AutoTokenizer
from collections import defaultdict

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

corpus = [
    "This is the Hugging Face course.",
    "This chapter is about tokenization.",
    "This section shows several tokenizer algorithms.",
    "Hopefully, you will be able to understand how they are trained and generate tokens.",
]


def calc_word_frequency(corpus: List[str]) -> dict:
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    word_freqs = defaultdict(int)
    for text in corpus:
        # pre_tokenizer: refer to course - https://huggingface.co/learn/nlp-course/chapter6/4
        words_with_offsets = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
        new_words = [word for word, offset in words_with_offsets]
        for word in new_words:
            word_freqs[word] += 1
    logger.debug(f"word frequency: {word_freqs}")
    return word_freqs


def construct_vocab(word_freqs: dict) -> list:
    alphabet = []
    for word in word_freqs.keys():
        if word[0] not in alphabet:
            alphabet += [word[0]]
        for char in word[1:]:
            if f"##{char}" not in alphabet:
                alphabet += [f"##{char}"]
    alphabet.sort()
    # supposing make the wordpiece tokenizer for BERT
    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + alphabet.copy()
    logger.debug(f"vocabulary: {vocab}")
    return vocab


def split_words(vocab: dict, word_freqs: dict) -> dict:
    splits = {word: [c if i == 0 else f"##{c}" for i, c in enumerate(word)] for word in word_freqs.keys()}
    logger.debug(f"splitted words: {splits}")
    return splits


def compute_pair_scores(splits: dict, word_freqs: dict) -> dict:
    char_freqs = defaultdict(int)
    pair_freqs = defaultdict(int)

    for word, freq in word_freqs.items():
        split = splits[word]
        if len(split) == 1:
            char_freqs[split[0]] += freq
            continue

        for i in range(len(split) - 1):
            pair = (split[i], split[i + 1])
            char_freqs[split[i]] += freq
            pair_freqs[pair] += freq

        char_freqs[split[-1]] += freq

    scores = {pair: freq / (char_freqs[pair[0]] * char_freqs[pair[1]]) for pair, freq in pair_freqs.items()}
    logger.debug(f"pair frequency: {scores}")
    return scores


def get_most_freq(pair_freqs: dict) -> tuple:
    most_pair = max(pair_freqs, key=pair_freqs.get)
    freq = pair_freqs[most_pair]
    return (most_pair, freq)


def merge_pair(first: str, second: str, splits: dict, word_freqs: dict) -> dict:
    for word in word_freqs:
        split = splits[word]
        if len(split) == 1:
            continue

        i = 0
        while i < len(split) - 1:
            if split[i] == first and split[i + 1] == second:
                merge = first + second[2:] if second.startswith("##") else first + second
                split = split[:i] + [merge] + split[i + 2 :]
            else:
                i += 1
        splits[word] = split
    return splits


def encode(word: str, vocab: list):
    tokens = []
    while len(word) > 0:
        i = len(word)
        while i > 0 and word[:i] not in vocab:
            i -= 1
        if i == 0:
            return ["[UNK]"]
        tokens += [word[:i]]
        word = word[i:]
        if len(word) > 0:
            word = f"##{word}"
    return tokens


def tokenize(text: str, vocab: list):
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    words_with_offsets = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
    encoded_words = [encode(word, vocab) for word, offset in words_with_offsets]
    return sum(encoded_words, [])


if __name__ == "__main__":
    word_freqs = calc_word_frequency(corpus)
    vocab = construct_vocab(word_freqs)
    splits = split_words(vocab, word_freqs)

    vocab_size = 70
    while len(vocab) < vocab_size:
        scores = compute_pair_scores(splits, word_freqs)

        # compute wordpiece pair scores
        pair_freqs = compute_pair_scores(splits, word_freqs)

        # get the most frequent pair comparing scores
        pair, freq = get_most_freq(pair_freqs)

        # merge the pair
        splits = merge_pair(*pair, splits, word_freqs)
        new_token = pair[0] + pair[1][2:] if pair[1].startswith("##") else pair[0] + pair[1]
        vocab.append(new_token)

    logger.info(f"trained vocab: {vocab}")

    logger.info(f"Encode 'Hugging': {encode('Hugging', vocab)}")
    logger.info(f"Encode 'hush': {encode('hush', vocab)}")

    logger.info(tokenize("wordpiece implementation course", vocab))
