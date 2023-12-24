import torch
import random
import logging
import pandas as pd
from typing import List
from torch.utils.data import Dataset
from transformers import AutoTokenizer

MODEL_NAME = "klue/roberta-base"
DATA_ROOT = "../data/"
DATA_PATH = DATA_ROOT + "smilestyle_dataset.tsv"


class PostDataset(Dataset):
    def __init__(self, data_path: str, ctx_len: int = 4):
        self.logger = self._set_logger()

        # set tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        special_tokens = {"sep_token": "<SEP>"}
        self.tokenizer.add_special_tokens(special_tokens)

        # construct sessions
        sessions = self._construct_sessions(data_path)

        # construct short sessions
        self.short_sessions = self._construct_short_sessions(sessions, ctx_len=ctx_len)

        # get all utterances
        self.all_utts = self._get_utterances(sessions)

    def __len__(self):
        return len(self.short_sessions)

    def __getitem__(self, idx):
        # Input data for MLM
        session = self.short_sessions[idx]
        mask_ratio = 0.15
        self.corrupt_tokens = []
        self.output_tokens = []
        for i, utt in enumerate(session):
            original_token = self.tokenizer.encode(utt, add_special_tokens=False)

            mask_num = int(len(original_token) * mask_ratio)
            mask_positions = random.sample([x for x in range(len(original_token))], mask_num)
            corrupt_token = []
            for pos in range(len(original_token)):
                if pos in mask_positions:
                    corrupt_token.append(self.tokenizer.mask_token_id)
                else:
                    corrupt_token.append(original_token[pos])

            if i == len(session) - 1:
                self.output_tokens += original_token
                self.corrupt_tokens += corrupt_token
            else:
                self.output_tokens += original_token + [self.tokenizer.sep_token_id]
                self.corrupt_tokens += corrupt_token + [self.tokenizer.sep_token_id]

        # Label for loss
        self.corrupt_mask_positions = []
        for pos in range(len(self.corrupt_tokens)):
            if self.corrupt_tokens[pos] == self.tokenizer.mask_token_id:
                self.corrupt_mask_positions.append(pos)

        # URC
        urc_tokens = []
        context_utts = []
        for i in range(len(session)):
            utt = session[i]
            original_token = self.tokenizer.encode(utt, add_special_tokens=False)
            if i == len(session) - 1:
                urc_tokens += [self.tokenizer.eos_token_id]
                self.positive_tokens = [self.tokenizer.cls_token_id] + urc_tokens + original_token
                while True:
                    random_neg_response = random.choice(self.all_utts)
                    if random_neg_response not in context_utts:
                        break
                random_neg_response_token = self.tokenizer.encode(random_neg_response, add_special_tokens=False)
                self.random_tokens = [self.tokenizer.cls_token_id] + urc_tokens + random_neg_response_token
                context_neg_response = random.choice(context_utts)
                context_neg_response_token = self.tokenizer.encode(context_neg_response, add_special_tokens=False)
                self.context_neg_tokens = [self.tokenizer.cls_token_id] + urc_tokens + context_neg_response_token
            else:
                urc_tokens += original_token + [self.tokenizer.sep_token_id]
            context_utts.append(utt)

        return (
            self.corrupt_tokens,
            self.output_tokens,
            self.corrupt_mask_positions,
            [self.positive_tokens, self.random_tokens, self.context_neg_tokens],
            [0, 1, 2],
        )

    def collate_fn(self, sessions):
        """
        input:
            data: [(session1), (session2), ... ]
        return:
            batch_corrupt_tokens: (B, L) padded
            batch_output_tokens: (B, L) padded
            batch_corrupt_mask_positions: list
            batch_urc_inputs: (B, L) padded
            batch_urc_labels: (B)
            batch_mlm_attentions
            batch_urc_attentions
        """
        batch_corrupt_tokens, batch_output_tokens, batch_corrupt_mask_positions, batch_urc_inputs, batch_urc_labels = (
            [],
            [],
            [],
            [],
            [],
        )
        batch_mlm_attentions, batch_urc_attentions = [], []

        corrupt_max_len, urc_max_len = 0, 0
        for session in sessions:
            corrupt_tokens, output_tokens, corrupt_mask_positions, urc_inputs, urc_labels = session
            if len(corrupt_tokens) > corrupt_max_len:
                corrupt_max_len = len(corrupt_tokens)
            positive_tokens, random_tokens, context_neg_tokens = urc_inputs
            if max([len(positive_tokens), len(random_tokens), len(context_neg_tokens)]) > urc_max_len:
                urc_max_len = max([len(positive_tokens), len(random_tokens), len(context_neg_tokens)])

        # add padding token
        for session in sessions:
            corrupt_tokens, output_tokens, corrupt_mask_positions, urc_inputs, urc_labels = session
            # mlm input
            batch_corrupt_tokens.append(
                corrupt_tokens + [self.tokenizer.pad_token_id for _ in range(corrupt_max_len - len(corrupt_tokens))]
            )
            batch_mlm_attentions.append(
                [1 for _ in range(len(corrupt_tokens))] + [0 for _ in range(corrupt_max_len - len(corrupt_tokens))]
            )

            # mlm output
            batch_output_tokens.append(
                output_tokens + [self.tokenizer.pad_token_id for _ in range(corrupt_max_len - len(corrupt_tokens))]
            )

            # mlm label
            batch_corrupt_mask_positions.append(corrupt_mask_positions)

            # urc input
            # positive_tokens, random_tokens, context_neg_tokens = urc_inputs
            for urc_input in urc_inputs:
                batch_urc_inputs.append(
                    urc_input + [self.tokenizer.pad_token_id for _ in range(urc_max_len - len(urc_input))]
                )
                batch_urc_attentions.append(
                    [1 for _ in range(len(urc_input))] + [0 for _ in range(urc_max_len - len(urc_input))]
                )

            # urc label
            batch_urc_labels += urc_labels
        return (
            torch.tensor(batch_corrupt_tokens),
            torch.tensor(batch_output_tokens),
            batch_corrupt_mask_positions,
            torch.tensor(batch_urc_inputs),
            torch.tensor(batch_urc_labels),
            torch.tensor(batch_mlm_attentions),
            torch.tensor(batch_urc_attentions),
        )

    def _set_logger(self):
        logging.basicConfig(
            format="%(message)s",
            level=logging.DEBUG,
        )
        logger = logging.getLogger()
        return logger

    def _construct_sessions(self, data_path: str) -> List[List[str]]:
        data = pd.read_csv(data_path, sep="\t")
        cols = data.columns.tolist()
        self.logger.debug(f"Columns: {cols}")

        # use formal conversational data
        data = data[["formal"]]
        data["group"] = data["formal"].isnull().cumsum()
        n_sessions = data["group"].iat[-1] + 1
        self.logger.debug(f"Number of groups: {n_sessions}")

        # split data into sessions
        sessions: List[List[str]] = []
        groups = data.groupby("group", as_index=False, group_keys=False)

        for i, group in groups:
            session = group.dropna()["formal"].tolist()
            sessions += [session]
        assert n_sessions == len(sessions)
        return sessions

    def _construct_short_sessions(self, sessions, ctx_len):
        short_sessions = []
        for session in sessions:
            for i in range(len(session) - ctx_len + 1):
                short_sessions.append(session[i : i + ctx_len])
        return short_sessions

    def _get_utterances(self, sessions):
        all_utts = set()
        for session in sessions:
            for utt in session:
                all_utts.add(utt)
        return list(all_utts)
