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
    """Matched part. (e.g., <table>, </p>)"""
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the match (e.g., source, attributes, relationships to other tags, etc.)"


@dataclass
class Node:
    indice: Tuple[int, int]
    """Indice tuple of start_idx and end_idx.
    start_idx is the first index of the target tag ('<' of '<table>'),
    end_idx is the last index of the closed target tag ('<' of '</table>')."""
    name: str
    """Name of tag. e.g., <table>, </p>"""
    child: List[Tag] = field(default_factory=list)
    """List of child tags of the tag."""
    parent: List[Tag] = field(default_factory=list)
    """List of parent tags of the tag."""
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the tag (e.g., source, attributes, relationships to other tag, etc.)"


@dataclass
class Chunk:
    indice: Tuple[int, int]
    """Indice tuple of chunk, which is one of the divided parts of the document."""
    content: str
    """String content between the indice."""
    metadata: dict = field(default_factory=dict)
    """Arbitrary metadata about the chunk (e.g., source, attributes, relationships to other chunk, etc.)"""


@dataclass
class Document:
    page: int
    page_content: str
    length: int
    metadata: dict = field(default_factory=dict)
    "Arbitrary metadata about the document (e.g., source, attributes, relationships to other tags, etc.)"
