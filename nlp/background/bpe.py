import re
import collections
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

num_merges = 10
vocab = {"l o w </w>": 5, "l o w e r </w>": 2, "n e w e s t </w>": 6, "w i d e s t </w>": 3}


def get_stats(vocab: dict):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        chars = word.split(" ")
        for i in range(len(chars) - 1):
            pairs[(chars[i], chars[i + 1])] += freq
    logger.debug(f"pair frequency: {dict(pairs)}")
    return pairs


def merge_vocab(pair: tuple, v_in: dict):
    v_out = dict()
    bigram = re.escape(" ".join(pair))
    p = re.compile(r"(?<!\S)" + bigram + r"(?!\S)")
    for word in v_in:
        w_out = p.sub("".join(pair), word)
        v_out[w_out] = v_in[word]
    return v_out


def encode(input: str, bpe_codes: dict):
    word = tuple(input) + ("</w>",)
    logger.info(f"'{input}' splitted into: {word}")

    def get_pairs(word: str):
        pairs = set()
        prev_char = word[0]
        for char in word[1:]:
            pairs.add((prev_char, char))
            prev_char = char
        return pairs

    pairs = get_pairs(word)
    if not pairs:
        return input

    iteration = 0
    while True:
        iteration += 1
        logger.debug(f"bigrams in the word: {pairs}")
        bigram = min(pairs, key=lambda pair: bpe_codes.get(pair, float("inf")))
        logger.info(f"candidate for merging: {bigram}")
        if bigram not in bpe_codes:
            logger.info(f"'{bigram}' not in BPE merge history. Stop merging.")
            break

        first, second = bigram
        new_word = []
        i = 0
        while i < len(word):
            try:
                j = word.index(first, i)
                new_word.extend(word[i:j])
                i = j
            except IndexError as e:
                logger.error(f"Index error occured. {e}")
                new_word.extend(word[i:])
                break

            if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                new_word.append(first + second)
                i += 2
            else:
                new_word.append(word[i])
                i += 1
        new_word = tuple(new_word)
        word = new_word
        logger.info(f"word after merging: {word}")
        if len(word) == 1:
            break
        else:
            pairs = get_pairs(word)

    if word[-1] == "</w>":
        word = word[:-1]
    elif word[-1].endswith("</w>"):
        word = word[:-1] + (word[-1].replace("</w>", ""),)

    return word


if __name__ == "__main__":
    # vocab merge history
    bpe_codes = {}

    for i in range(num_merges):
        pairs = get_stats(vocab)
        most = max(pairs, key=pairs.get)
        vocab = merge_vocab(most, vocab)

        bpe_codes[most] = i

        logger.info(f"{i+1}th merged pair: {most}")
        logger.info(f"{i+1}th vocab: {vocab}")

    # encode lowest, loki
    encoded_word = encode("lowest", bpe_codes=bpe_codes)
    logger.info(f"result: {encoded_word}")

    encoded_word = encode("loki", bpe_codes=bpe_codes)
    logger.info(f"result: {encoded_word}")
