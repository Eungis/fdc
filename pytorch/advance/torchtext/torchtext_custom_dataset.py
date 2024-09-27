import os
from torchtext import data

src = data.Field(sequential=True, use_vocab=True, batch_first=True, include_lengths=True)

tgt = data.Field(
    sequential=True, use_vocab=True, batch_first=True, include_lengths=True, init_token="<BOS>", eos_token="<EOS>"
)

fields = [("src", src), ("tgt", tgt)]

# train_fn
# corpus.en
# corpus.ko


class TranslationDataset(data.Dataset):
    """
    Load source data and target data given paths and fields
    ** Attention: Here path of the data is not tabular data
    """

    def __init__(self, path, exts, fields, max_length):
        if not path.endswith("."):
            path += "."

        if not isinstance(fields[0], (tuple, list)):
            fields = [("src", src), ("tgt", tgt)]

        src_path, tgt_path = [os.path.expanduser(path + x) for x in exts]
        examples = []

        with open(src_path, encoding="utf-8") as src_file, open(tgt_path, encoding="utf-8") as tgt_file:
            for src_line, tgt_line in zip(src_file, tgt_file):
                src_line, tgt_line = src_line.strip(), tgt_line.strip()
                if src_line != "" and tgt_line != "":
                    examples += [data.Example.fromlist([src_line, tgt_line], fields)]

        super().__init__(examples, fields, filter_pred=lambda x: len(x.src) < max_length)


if __name__ == "__main__":
    train = TranslationDataset(
        path="./data/practice/corpus", exts=["en", "ko"], fields=[("src", src), ("tgt", tgt)], max_length=256
    )

    src.build_vocab(train, max_size=999999)
    tgt.build_vocab(train, max_size=999999)

    device = -1

    train_loader = data.BucketIterator(
        train,
        batch_size=128,
        device="cuda:%d" % device if device >= 0 else "cpu",
        shuffle=True,
        sort_key=lambda x: len(x.tgt) + (256 * len(x.src)),
        sort_within_batch=True,
    )

    batch = next(iter(train_loader))
    print(type(batch.src))
    print(batch.src[0].shape, batch.src[1].shape)
