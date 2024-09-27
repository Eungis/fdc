from torchtext import data


class DataLoader:
    def __init__(
        self,
        train_fn,
        batch_size=64,
        valid_ratio=0.2,
        device=-1,
        max_vocab=999999,
        min_freq=1,
        use_eos=False,
        shuffle=True,
    ):
        """
        DataLoader initialization.
        :param train_fn: Train-set filename
        :param batch_size: Batchify data fot certain batch size.
        :param device: Device-id to load data (-1 for CPU)
        :param max_vocab: Maximum vocabulary size
        :param min_freq: Minimum frequency for loaded word.
        :param use_eos: If it is True, put <EOS> after every end of sentence.
        :param shuffle: If it is True, random shuffle the input data.
        """
        super().__init__()

        # Define field of the input file.
        # The input file consists of two fields.
        # data.Field: https://torchtext.readthedocs.io/en/latest/data.html
        # data.Field: https://pytorch.org/text/_modules/torchtext/data/field.html
        self.label = data.Field(
            sequential=False,  # if True: tokenization
            use_vocab=True,  # if False: the data in this field should already be numerical
            unk_token=None,
        )

        self.text = data.Field(
            use_vocab=True, batch_first=True, include_lengths=False, eos_token="<EOS>" if use_eos else None
        )

        # data.Dataset: https://torchtext.readthedocs.io/en/latest/data.html
        train, valid = data.TabularDataset(
            path=train_fn, format="tsv", fields=[("label", self.label), ("text", self.text)]
        ).split(split_ratio=(1 - valid_ratio))

        self.train_loader, self.valid_loader = data.BucketIterator.splits(
            (train, valid),
            batch_size=batch_size,
            device="cuda:%d" % device if device >= 0 else "cpu",
            sort_key=lambda x: len(x.text),
            shuffle=shuffle,  # Whether to shuffle examples between epochs.
            sort_within_batch=True,  # whether to sort examples in descending order according to the sort_key
        )

        # At last, we make a vocabulary for label and text field.
        # It is making mapping table between words and indice.
        self.label.build_vocab(train)
        self.text.build_vocab(train, max_size=max_vocab, min_freq=min_freq)
