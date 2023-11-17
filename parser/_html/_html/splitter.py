from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable
from dataclasses import dataclass
from uuid import uuid4
from bs4 import BeautifulSoup

from _html.schema import Tag, Node, Chunk, Document


@dataclass
class Splitter(object):
    soup: BeautifulSoup
    length_func: Callable[[str], int]
    token_max: int
    chunk_size: int = 2

    def __post_init__(self):
        # get document from the BeautifulSoup object
        doc = self.soup.prettify().strip()
        self.doc = self._cleanse_soup_tags(doc)

        # get all tags from the BeautifulSoup object
        self.tags = [tag.name for tag in self.soup.find_all()]
        self.tags = list(set(self.tags))

        # initialize the node list and chunk list
        self.nodes, self.chunks = [], []

    def _cleanse_soup_tags(self, doc: str) -> str:
        pat = re.compile(r"<.*html>|<*.body>")
        doc = re.sub(pat, "", doc)
        return doc.strip()

    def find_nodes(self, tag):
        tag_counter = defaultdict(int)
        nodes = []

        pat = re.compile(rf"<.*{tag}>")
        match = pat.search(self.doc)

        tags = []
        while match:
            # get matched_tag. e.g. <table>, </table>
            matched_tag = match.group(0)
            # count depth of matched_tag to do pairing later
            tag_counter[matched_tag] += 1
            depth = tag_counter[matched_tag]
            tags += [Tag(indice=match.span(), name=matched_tag, metadata={"depth": depth})]
            # get pair_tag. e.g, <table> -> </table>
            pair_matched_tag = rf"</{tag}>" if r"/" not in matched_tag else matched_tag.replace(r"/", "")

            # recognize as Node if depth tags with each other
            if depth == tag_counter[pair_matched_tag]:
                # pairing tags according to the matching depth
                tags = sorted(tags, key=lambda x: x.metadata["depth"])
                start, end = tags[0], tags[-1]
                indice = start.indice + end.indice
                start_idx, end_idx = min(indice), max(indice)
                tag_name = start.name
                id = str(uuid4())
                nodes += [Node(indice=(start_idx, end_idx), name=tag_name, metadata={"id": id})]
                # reset after chunking done
                tags = []
                tag_counter[matched_tag], tag_counter[pair_matched_tag] = 0, 0
            match = pat.search(self.doc, match.start() + 1)

        return nodes

    def _add_relationship_to_node(self, node) -> None:
        start, end = node.indice

        # get parent candidates
        parent_cands = []
        # exclude the self from the list
        # note. the node with the same name (tag name) cannot be its parent
        _nodes = [_node for _node in self.nodes if _node != node and _node.name != node.name]
        for _node in _nodes:
            _start, _end = _node.indice
            if _start < start and _end > end:
                parent_cands += [_node]

        # get neareast parent from the candidates
        if len(parent_cands) > 0:
            parent = parent_cands[0]
            min_gap = abs(parent.indice[0] - start)
            for cand in parent_cands:
                _gap = abs(cand.indice[0] - start)
                if _gap < min_gap:
                    parent = cand
                    min_gap = _gap

            # add parent and child information to each other
            parent.child += [node.metadata["id"]]
            node.parent += [parent.metadata["id"]]

    def _get_node_from_id(self, id):
        for node in self.nodes:
            if id == node.metadata["id"]:
                return node

    def _update_nodes(self):
        for node in self.nodes:
            childs = [self._get_node_from_id(id) for id in node.child]
            parents = [self._get_node_from_id(id) for id in node.parent]
            childs = sorted(childs, key=lambda x: x.indice[0], reverse=False)
            parents = sorted(parents, key=lambda x: x.indice[0], reverse=False)

            node.child = childs
            node.parent = parents

    def _get_no_parent_nodes(self):
        _tags = [_tag for _tag in self.nodes if len(_tag.parent) == 0]
        _tags = sorted(_tags, key=lambda x: x.indice[0], reverse=False)
        return _tags

    def get_chunks(self):
        # get nodes of the tag in the document
        for tag in self.tags:
            self.nodes.extend(self.find_nodes(tag))

        # update parent and child relationship
        for node in self.nodes:
            self._add_relationship_to_node(node)
        self._update_nodes()
        chunk_nodes = self._get_no_parent_nodes()

        # append to chunks
        start = 0
        for node in chunk_nodes:
            _start, _end = node.indice
            if start != _start:
                self.chunks += [
                    Chunk(indice=(start, _start), content=self.doc[start:_start], metadata={"type": "string"})
                ]
            self.chunks += [Chunk(indice=(_start, _end), content=self.doc[_start:_end], metadata={"type": node.name})]
            start = _end

        return self.chunks

    def _split_chunk(self, chunk):
        # split chunk into several parts and recombine them
        if chunk.metadata["type"] == "<table>":
            soup = BeautifulSoup(chunk.content, "lxml")
            table = soup.find("table")

            all_rows = table.find_all("tr")

            _chunks = []
            for i in range(0, len(all_rows), self.chunk_size):
                _chunk = all_rows[i: i + self.chunk_size]
                # Create a new table for each chunk
                new_table = soup.new_tag("table")
                new_table.extend(_chunk)

                _chunks += [
                    Chunk(
                        indice=(0, 0),  # [TODO] how to specify indice
                        content=new_table.prettify(),
                        metadata={"type": "<table>"},
                    )
                ]

        return _chunks

    def split_chunks(self, chunks):
        prev_chunk_size = self.chunk_size
        lengths = [self.length_func(chunk.content) for chunk in chunks]
        new_chunks = []
        for chunk, length in zip(chunks, lengths):
            if length > self.token_max:
                # check single chunk exceeds the self.token_max
                # if true: recursively split the chunk into several chunks according to the split_chunk function.
                while length is not None and length > self.token_max:
                    splitted_chunks = self._split_chunk(chunk)
                    # count the maximum num_token of splitted chunks
                    length = max([self.length_func(chunk.content) for chunk in splitted_chunks])
                    # increase the chunk_size
                    self.chunk_size += 1
                self.chunk_size = prev_chunk_size
                new_chunks.extend(splitted_chunks)
            else:
                new_chunks.append(chunk)
        return new_chunks

    def merge_into_documents(self, chunks):
        new_docs = []
        _sub_chunks = []
        lengths = [self.length_func(chunk.content) for chunk in chunks]
        cum_length, page_cnt = 0, 0

        for chunk, length in zip(chunks, lengths):
            _sub_chunks.append(chunk)
            cum_length += length
            if cum_length > self.token_max:
                document = Document(
                    page=page_cnt,
                    page_content="".join([chunk.content for chunk in _sub_chunks[:-1]]),
                    length=cum_length - length,
                )
                new_docs += [document]
                page_cnt += 1
                _sub_chunks = _sub_chunks[-1:]
                cum_length = length
        document = Document(
            page=page_cnt, page_content="".join([chunk.content for chunk in _sub_chunks]), length=cum_length
        )
        new_docs += [document]
        return new_docs
