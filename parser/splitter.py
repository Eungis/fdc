from __future__ import annotations
import re
from collections import defaultdict
from typing import Tuple, List
from dataclasses import dataclass, field
from uuid import uuid4
from bs4 import BeautifulSoup


@dataclass
class Match:
    indice: Tuple[int, int]
    "indice tuple of start_idx and end_idx."
    match: str
    "matched part"
    metadata: dict = field(default_factory=dict)
    "arbitrary metadata about the match (e.g., source, attributes, relationships to other matches, etc.)"


@dataclass
class Tag:
    indice: Tuple[int, int]
    name: str
    child: List[Tag] = field(default_factory=list)
    parent: List[Tag] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    "arbitrary metadata about the page content (e.g., source, attributes, relationships to other matches, etc.)"


@dataclass
class Chunk:
    indice: Tuple[int, int]
    content: str
    metadata: dict = field(default_factory=dict)


def find_tag_bundle(txt, tag):
    tags = []
    tag_counter = defaultdict(int)

    pat = re.compile(rf"<.*{tag}>")
    match = pat.search(txt)

    matches = []
    while match:
        # get matched_tag. e.g. <table>, </table>
        matched_tag = match.group(0)
        # count depth of matched_tag to do pairing later
        tag_counter[matched_tag] += 1
        depth = tag_counter[matched_tag]
        matches += [Match(indice=match.span(), match=matched_tag, metadata={"depth": depth})]
        # get pair_tag. e.g, <table> -> </table>
        pair_matched_tag = rf"</{tag}>" if r"/" not in matched_tag else matched_tag.replace(r"/", "")

        # recognize as Tag if depth matches with each other
        if depth == tag_counter[pair_matched_tag]:
            # pairing matches according to the matching depth
            matches = sorted(matches, key=lambda x: x.metadata["depth"])
            start, end = matches[0], matches[-1]
            indice = start.indice + end.indice
            start_idx, end_idx = min(indice), max(indice)
            tag_name = start.match
            id = str(uuid4())
            tags += [Tag(indice=(start_idx, end_idx), name=tag_name, metadata={"id": id})]
            # reset after chunking done
            matches = []
            tag_counter[matched_tag], tag_counter[pair_matched_tag] = 0, 0
        match = pat.search(txt, match.start() + 1)
    return tags


def add_relationship_to_tag(tag, tags) -> None:
    start, end = tag.indice

    parent_cands = []
    _tags = [_tag for _tag in tags if _tag != tag and _tag.name != tag.name]
    for _tag in _tags:
        _start, _end = _tag.indice
        if _start < start and _end > end:
            parent_cands += [_tag]

    # get neareast parent
    if len(parent_cands) > 0:
        parent = parent_cands[0]
        min_gap = abs(parent.indice[0] - start)
        for cand in parent_cands:
            _gap = abs(cand.indice[0] - start)
            if _gap < min_gap:
                parent = cand
                min_gap = _gap

        parent.child += [tag.metadata["id"]]
        tag.parent += [parent.metadata["id"]]


def get_tag_from_id(id, tags):
    for tag in tags:
        if id == tag.metadata["id"]:
            return tag


def update_tags(tags):
    for tag in tags:
        childs = [get_tag_from_id(id, tags) for id in tag.child]
        parents = [get_tag_from_id(id, tags) for id in tag.parent]
        childs = sorted(childs, key=lambda x: x.indice[0], reverse=False)
        parents = sorted(parents, key=lambda x: x.indice[0], reverse=False)

        tag.child = childs
        tag.parent = parents


def get_no_parent_tags(tags):
    _tags = [_tag for _tag in tags if len(_tag.parent) == 0]
    _tags = sorted(_tags, key=lambda x: x.indice[0], reverse=False)
    return _tags


def get_chunks(txt, tags):
    start = 0
    chunks = []
    for tag in tags:
        _start, _end = tag.indice
        chunks += [Chunk(indice=(start, _start), content=txt[start:_start])]
        chunks += [Chunk(indice=(_start, _end), content=txt[_start:_end])]
        start = _end
    return chunks


if __name__ == "__main__":

    def make_data(txt):
        soup = BeautifulSoup(txt, "lxml")
        txt = soup.prettify()
        return txt

    def clean_soup_tags(doc: str) -> str:
        pat = re.compile(r"<.*html>|<*.body>")
        doc = re.sub(pat, "", doc)
        return doc.strip()

    def leave_valid_tags(doc: str, valid_tags: list) -> str:
        soup = BeautifulSoup(doc, "lxml")
        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0 and x.name not in valid_tags:
                x.extract()
        return soup.prettify()

    with open("../data/html_ex.txt", "r") as f:
        data = f.read()

    txt = make_data(data)

    valid_tags = ["p", "table", "th", "tr", "td", "img"]
    txt = leave_valid_tags(txt, valid_tags)
    txt = clean_soup_tags(txt)

    tags = []
    for html_tag in ["table", "tr", "td"]:
        tags.extend(find_tag_bundle(txt, html_tag))

    for tag in tags:
        add_relationship_to_tag(tag, tags)
    update_tags(tags)
    tags = get_no_parent_tags(tags)
    chunks = get_chunks(txt, tags)

    assert "".join([chunk.content for chunk in chunks]) == txt
