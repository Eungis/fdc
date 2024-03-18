from __future__ import annotations
from typing import Tuple, List
from dataclasses import dataclass, field


@dataclass
class Tag:
    indice: Tuple[int, int]
    """Indice tuple of start_idx and end_idx.
    start_idx is the first index of the target tag ('<' of '<table>'),
    end_idx is the last index of the target tag ('>' of '<table>')."""
    name: str
    """Matched part of r"<.*{tag}>". (e.g., <table>, </p>)"""
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the tag (e.g., source, attributes, relationships to other tags, etc.)"


@dataclass
class Node:
    """Node is the whole content between html tags, which has no any parent tag above it.
    and the base content that should be thought of as a meaningful part."""

    indice: Tuple[int, int]
    """Indice tuple of start_idx and end_idx.
    start_idx is the first index of the target tag ('<' of '<table>'),
    end_idx is the last index of the closed target tag ('<' of '</table>')."""
    name: str
    """Name of tag. e.g., <table>, <p>"""
    child: List[Node] = field(default_factory=list)
    """List of child nodes of the node."""
    parent: List[Node] = field(default_factory=list)
    """List of parent nodes of the node."""
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the Node (e.g., source, attributes, relationships to other node, etc.)"


@dataclass
class Chunk:
    indice: Tuple[int, int]
    """Indice tuple of start_idx and end_idx, which is one of the divided parts of the document."""
    content: str
    """String content between the indice."""
    metadata: dict = field(default_factory=dict)
    """Arbitrary metadata about the chunk (e.g., source, attributes, relationships to other chunk, etc.)"""


@dataclass
class Document:
    page: int
    """Page index of the documents."""
    page_content: str
    """Content of the page."""
    length: int
    """Length counted through length_func."""
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the document (e.g., source, attributes, relationships to other documents, etc.)"
