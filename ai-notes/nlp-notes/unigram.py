#!/Users/cho-eungi/miniforge3/envs/nlp/bin/python
import logging
import math
import copy
from typing import List
from transformers import AutoTokenizer
from collections import defaultdict

corpus = [
    "This is the Hugging Face course.",
    "This chapter is about tokenization.",
    "This section shows several tokenizer algorithms.",
    "Hopefully, you will be able to understand how they are trained and generate tokens.",
]

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def calc_word_frequency(corpus: List[str]) -> dict:
    tokenizer = AutoTokenizer.from_pretrained("xlnet-base-cased")
    word_freqs = defaultdict(int)
    for text in corpus:
        # pre_tokenizer: refer to course - https://huggingface.co/learn/nlp-course/chapter6/4
        words_with_offsets = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
        new_words = [word for word, offset in words_with_offsets]
        for word in new_words:
            word_freqs[word] += 1
    logger.debug(f"word frequency: {word_freqs}")
    return word_freqs


def construct_vocab(word_freqs: dict, init_vocab_size=300) -> dict:
    # Note. Sentencepiece uses the algorithm known as ESA (Enhanced Suffix Array)
    # to build vocabulary.
    char_freqs = defaultdict(int)
    subwords_freqs = defaultdict(int)
    for word, freq in word_freqs.items():
        for i in range(len(word)):
            char_freqs[word[i]] += freq
            for j in range(i + 2, len(word) + 1):
                subwords_freqs[word[i:j]] += freq
    sorted_subwords = sorted(subwords_freqs.items(), key=lambda x: x[1], reverse=True)
    logger.debug(f"subwords_freqs: {sorted_subwords[:10]}")
    # do not forget to add char_freqs as tokens to vocabulary
    # to enable the tokenizer to tokenize all the words.
    # that means, we never remove the base characters.
    token_freqs = list(char_freqs.items()) + sorted_subwords[: init_vocab_size - len(char_freqs)]
    token_freqs = {token: freq for token, freq in token_freqs}
    return token_freqs


def encode_word(word, model):
    best_segmentations = [{"start": 0, "score": 1}] + [{"start": None, "score": None} for _ in range(len(word))]
    for start_idx in range(len(word)):
        best_score_at_start = best_segmentations[start_idx]["score"]
        for end_idx in range(start_idx + 1, len(word) + 1):
            token = word[start_idx:end_idx]
            if token in model and best_score_at_start is not None:
                score = model[token] + best_score_at_start  # due to -math.log(prob), use + instead of *
                # if a better segmentation ending at end_idx was found, update it
                if best_segmentations[end_idx]["score"] is None or best_segmentations[end_idx]["score"] > score:
                    best_segmentations[end_idx] = {"start": start_idx, "score": score}
                logger.debug(
                    f"token: {token} | start, end: {start_idx, end_idx} | score: {model[token]} | best_score_at_start: {best_score_at_start}"
                )
            else:
                pass

    segmentation = best_segmentations[-1]
    if segmentation["score"] is None:
        return ["<unk>"], None

    score = segmentation["score"]
    start = segmentation["start"]
    end = len(word)
    tokens = []
    while start != 0:
        tokens.insert(0, word[start:end])
        next_start = best_segmentations[start]["start"]
        end = start
        start = next_start
    tokens.insert(0, word[start:end])
    return tokens, score


def compute_scores(model, word_freqs):
    def compute_loss(model, word_freqs):
        loss = 0
        for word, freq in word_freqs.items():
            _, word_loss = encode_word(word, model)
            loss += freq * word_loss
        return loss

    scores = {}
    model_loss = compute_loss(model, word_freqs)
    for token, score in model.items():
        if len(token) == 1:
            continue
        model_wo_token = copy.deepcopy(model)
        _ = model_wo_token.pop(token)
        scores[token] = compute_loss(model_wo_token, word_freqs) - model_loss
    return scores


def tokenize(text, model):
    tokenizer = AutoTokenizer.from_pretrained("xlnet-base-cased")
    # pre_tokenize
    words_with_offsets = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
    pre_tokenized_text = [word for word, offset in words_with_offsets]
    # subword_tokenization using unigram
    encoded_words = [encode_word(word, model)[0] for word in pre_tokenized_text]
    return sum(encoded_words, [])


if __name__ == "__main__":
    word_freqs = calc_word_frequency(corpus)
    vocab = construct_vocab(word_freqs)
    total_sum = sum(vocab.values())
    # it's more stable to add logarithms than to multiply small numbers
    # to compute the probability of tokens according to the unigram model.
    # note. it's regardless of computing total loss of corpus.
    model = {token: -math.log(freq / total_sum) for token, freq in vocab.items()}
    logger.debug(f"model: {model}")

    print(encode_word("Hopefully", model))

    vocab_size = 120
    percent_to_remove = 0.1
    while len(model) > vocab_size:
        scores = compute_scores(model, word_freqs)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        for i in range(int(len(model) * percent_to_remove)):
            _ = vocab.pop(sorted_scores[i][0])

        total_sum = sum(vocab.values())
        model = {token: -math.log(freq / total_sum) for token, freq in vocab.items()}
        logger.info(f"remaining vocab_size: {len(model)}")

    print(tokenize("unigram tokenization course", model))
