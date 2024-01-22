from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable, List
from dataclasses import dataclass, field
from bs4 import BeautifulSoup

from _html.schema import Tag, Node, Chunk, Document


@dataclass
class HTMLSplitter(object):
    soup: BeautifulSoup
    """BeautifulSoup object to parse."""
    length_func: Callable[[str], int]
    """Length function to count the number of tokens."""
    token_max: int
    """Maximum token that a document can have."""
    chunks: List[Chunk] = field(default_factory=list)
    """List of splitted chunks."""
    split_denominator: int = 2
    """Denominator to use during _split_chunk."""
    split_trial_max: int = 5
    """Maximum number of trials to split the single chunk."""
    raise_error: bool = True
    """Whether to raise error if any of the chunk is not splittable even with max trials."""

    """Separate the html soup object into the tags > nodes > chunks > documents.

    Four schemas are defined and used: tag, node, chunk and document.
    (it's completely different from the BeautifulSoup schema.)

    - `tag` refers to the start or closed tag of the html. e.g. '<table>', '</p>'
    - `node` refers to the html tag which has no parent tags above it.
    cf. <html> and <body> tags are not thought of as parents.
    - `chunk` refers to the chunk(part) of the document which may be the
    part before, in-between, after the node; or the node itself.
    - `document` refers to the combined chunks according to the token_max.

    A single chunk of which length exceeds the token_max would be separated
    into several chunks, and be made as multiple documents. See `split_chunks`
    with more details;

    A single chunk of which length does not exceed the token_max would be
    fed to merge with the next chunk, continuously. When the length of
    the merged chunks exceed the token_max, it would stop the cohesion and be
    made as a single document. See `make_documents` with more details.

    [Attention]
    Internally, it uses regular expression to detect the html tags.
    Therefore, if the text you provided contains the string '<{tag}>', which
    is not true tag of the html, HTMLSplitter will be confused and identify it as
    real tag, and result in the error.
    (e.g. "<div>A real div tag</div>\nThis is the fake <div> tag.\n<div>Another real div tag</div>")

    Example:
        .. code-block:: python

            from bs4 import BeautifulSoup
            from _html.cleanser import HTMLCleanser
            from _html.splitter import Splitter

            soup = BeautifulSoup("YOUR_HTML", "lxml")
            cleanser = HTMLCleanser()

            # cleanse the html
            soup = cleanser.cleanse_html(soup)

            # split the soup html into the documents
            splitter = Splitter(soup=soup, length_func=len, token_max=1500)
            tags = splitter.get_tags_from_soup(soup)
            chunks = splitter.get_chunks(tags)
            new_chunks = splitter.split_chunks(chunks)
            documents = splitter.make_documents(new_chunks)
    """

    def _cleanse_soup_tags(self) -> str:
        html = self.soup.prettify().strip()
        pat = re.compile(r"<.*html>|<*.body>")
        html = re.sub(pat, "", html).strip()
        return html

    def get_tags_in_soup(self) -> List[str]:
        tags = [tag.name for tag in self.soup.find_all()]
        tags = list(set(tags))
        return tags

    def __post_init__(self):
        self.html = self._cleanse_soup_tags()
        self.tags = self.get_tags_in_soup()

    def find_nodes(self, tag: str) -> List[Node]:
        """Find the nodes of which tag name is equal as given `tag`.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of Nodes

        Example:
            .. code-block:: python
            txt="YOUR_HTML"
            soup = BeautifulSoup(txt, 'lxml')
            splitter = HTMLSplitter(soup, length_func=len, token_max=1500)
            nodes = splitter.find_nodes('table')
        """
        tag_counter = defaultdict(int)
        nodes = []

        pat = re.compile(rf"<.*{tag}>")
        match = pat.search(self.html)

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
                nodes += [Node(indice=(start_idx, end_idx), name=tag_name)]
                # reset after chunking done
                tags = []
                tag_counter[matched_tag], tag_counter[pair_matched_tag] = 0, 0
            match = pat.search(self.html, match.start() + 1)

        return nodes

    def _find_parent_child_nodes(self, node: Node, nodes: List[Node]) -> None:
        start, end = node.indice

        # initialize parent candidates
        parent_cands = []
        # exclude the self from the list
        # note. the node with the same name (tag name) cannot be its parent
        _nodes = [_node for _node in nodes if _node != node and _node.name != node.name]
        for _node in _nodes:
            _start, _end = _node.indice
            if _start < start and _end > end:
                parent_cands += [_node]

        # find neareast parent from the candidates
        if len(parent_cands) > 0:
            parent = parent_cands[0]
            min_gap = abs(parent.indice[0] - start)
            for cand in parent_cands:
                gap = abs(cand.indice[0] - start)
                if gap < min_gap:
                    parent = cand
                    min_gap = gap

            # add parent and child information to each other
            parent.child += [node]
            node.parent += [parent]

    def _sort_parent_child_nodes(self, nodes: List[Node]):
        for node in nodes:
            childs = sorted(node.child, key=lambda x: x.indice[0], reverse=False)
            parents = sorted(node.parent, key=lambda x: x.indice[0], reverse=False)

            node.child = childs
            node.parent = parents
        return nodes

    def _get_chunk_nodes(self, nodes: List[Node]):
        # filter and get the nodes with no parents,
        # which are considered as chunks of html.
        _nodes = [node for node in nodes if len(node.parent) == 0]
        _nodes = sorted(_nodes, key=lambda x: x.indice[0], reverse=False)
        return _nodes

    def get_chunks(self) -> List[Chunk]:
        """Split the html into several chunks.

        Args:

        Returns:
            List of Chunks

        Example:
            .. code-block:: python
            txt="YOUR_HTML"
            soup = BeautifulSoup(txt, 'lxml')
            splitter = HTMLSplitter(soup, length_func=len, token_max=1500)
            chunks = splitter.get_chunks()
            assert ''.join([chunk.content for chunk in chunks]) == splitter.html
        """

        # find nodes
        nodes = []
        for tag in self.tags:
            nodes.extend(self.find_nodes(tag))

        # update parent and child relationship of each node
        for node in nodes:
            self._find_parent_child_nodes(node, nodes)
        # sort according to the start index of the child or parent nodes
        nodes = self._sort_parent_child_nodes(nodes)
        # get chunk_nodes
        chunk_nodes = self._get_chunk_nodes(nodes)

        # append to chunks
        start = 0
        for node in chunk_nodes:
            _start, _end = node.indice
            if start != _start:
                self.chunks += [
                    Chunk(indice=(start, _start), content=self.html[start:_start], metadata={"type": "string"})
                ]
            _type = re.sub(r"<|>", "", node.name)
            self.chunks += [Chunk(indice=(_start, _end), content=self.html[_start:_end], metadata={"type": _type})]
            start = _end

        return self.chunks

    def _split_chunk(self, chunk: Chunk) -> List[Chunk]:
        """Split a single chunk, of which length is larger than token_max,
        into several parts, and recombine them at the end.into several chunks.

        Args:
            chunk: chunk of the document
        Returns:
            List of chunks
        """

        def make_rows_as_table(soup, th_rows, rows):
            table = soup.new_tag("table")
            table.extend(th_rows)
            table.extend(rows)
            return table

        _chunks = []

        if chunk.metadata["type"] == "table":
            soup = BeautifulSoup(chunk.content, "lxml")
            table = soup.find("table")

            # separate rows with general `rows` and `th rows`
            all_rows = table.find_all("tr")
            th_rows = []
            for i, row in enumerate(all_rows):
                if len(row.find_all("th")) > 0:
                    th_rows += [all_rows.pop(i)]

            # divide the single chunk into chunks
            quotient = len(all_rows) // self.split_denominator
            quotient = 1 if quotient == 0 else quotient

            for i in range(0, len(all_rows), quotient):
                rows = all_rows[i : i + quotient]
                new_table = make_rows_as_table(soup, th_rows, rows)
                _chunks += [
                    Chunk(
                        indice=None,  # [TODO] how to specify indice
                        content=new_table.prettify(),
                        metadata={"type": "table"},
                    )
                ]
        # overide here if you have your own valid tags.
        # chunk.metadata["type"] == "string"
        else:
            sentences: List[str] = chunk.content.split(".")

            quotient = len(sentences) // self.split_denominator
            quotient = 1 if quotient == 0 else quotient

            for i in range(0, len(sentences), quotient):
                new_chunk = ". ".join(sentences[i : i + quotient])
                _chunks += [Chunk(indice=(0, 0), content=new_chunk, metadata={"type": "string"})]
        return _chunks

    def split_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Iterate over all the chunks and separate them
        to guarantee that there is no any length of the chunk
        exceeds the token_max

        Args:
            chunks: List of chunks
        Returns:
            List of chunks
        """
        lengths = [self.length_func(chunk.content) for chunk in chunks]
        new_chunks = []
        for chunk, length in zip(chunks, lengths):
            if length > self.token_max:
                n_trial = 1
                # check single chunk exceeds the token_max
                # if true, recursively split the chunk into several chunks
                # until length of each chunk does not exceed the token_max
                while length is not None:
                    if n_trial > self.split_trial_max:
                        # raise error or append the chunk as it is
                        if self.raise_error:
                            raise ValueError(
                                f"Chunk is not splittable even with {self.split_trial_max} trials.\n \
    The length of the splitted chunk is still longer than the token_max.\n \
    Increase the token_max, or see if the Chunk is splittable.\n \
    chunk indice: {chunk.indice}\n \
    chunk type: {chunk.metadata.get('type')}"
                            )
                        else:
                            print(
                                f"The length of chunk `{chunk.metadata.get('type')}: {chunk.indice}` "
                                "exceeds the token_max, but failed to split the chunk.\n"
                                "A single row of the table may exceed the token_max, \n"
                                f"or the split function for {chunk.metadata.get('type')} has not been developped."
                            )
                            new_chunks.append(chunk)
                            break
                    splitted_chunks = self._split_chunk(chunk)

                    # count the num_token of splitted chunks
                    length = None
                    for _chunk in splitted_chunks:
                        chunk_length = self.length_func(_chunk.content)
                        if chunk_length > self.token_max:
                            length = chunk_length
                            break
                    # increase the split_denominator and trial_cnt
                    self.split_denominator += 1
                    n_trial += 1

                new_chunks.extend(splitted_chunks)
            else:
                new_chunks.append(chunk)
        return new_chunks

    def make_documents(self, chunks: List[Chunk]) -> List[Document]:
        """Merge separated chunks into the set of documents
        before putting into the llm model.
        It takes into account of the token_max and merges the chunks
        continuously, until the length of the merged chunks does not
        exceed the token_max.

        Args:
            chunks: List of chunks
        Returns:
            List of documents
        """
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
