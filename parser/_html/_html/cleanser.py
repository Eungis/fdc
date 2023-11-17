import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from _html.constant import DEFAULT_VALID_ATTRS, DEFAULT_VALID_TAGS


class HTMLCleanser:
    def __init__(self, valid_tags: List[str] = None, valid_attrs: List[str] = None):
        self.__valid_tags = DEFAULT_VALID_TAGS if valid_tags is None else valid_tags
        self.__valid_attrs = DEFAULT_VALID_ATTRS if valid_attrs is None else valid_attrs
        print(f"""valid_tags: {self.__valid_tags}\nvalid_attrs: {self.__valid_attrs}""")

    @property
    def valid_tags(self):
        return self.__valid_tags

    @property
    def valid_attrs(self):
        return self.__valid_attrs

    @valid_tags.setter
    def valid_tags(self, valid_tags):
        self.__valid_tags = valid_tags

    @valid_attrs.setter
    def valid_attrs(self, valid_attrs):
        self.__valid_attrs = valid_attrs

    def add_valid_tags(self, tags: List[str]):
        tag_sets = set(self.valid_tags)
        tag_sets.update(tags)
        self.valid_tags = list(tag_sets)
        return self.valid_tags

    def add_valid_attrs(self, attrs: List[str]):
        attr_sets = set(self.valid_attrs)
        attr_sets.update(attrs)
        self.valid_attrs = list(attr_sets)
        return self.valid_attrs

    def remove_valid_tags(self, tags: List[str]):
        self.valid_tags = [tag for tag in self.valid_tags if tag not in tags]
        return self.valid_tags

    def remove_valid_attrs(self, attrs: List[str]):
        self.valid_attrs = [attr for attr in self.valid_attrs if attr not in attrs]
        return self.valid_attrs

    def _get_invalid_tags_attrs(self, soup: BeautifulSoup) -> Tuple[list, list]:
        tags, attrs = set(), set()
        for tag in soup.find_all():
            tags.add(tag.name)
            attrs.update(list(tag.attrs.keys()))

        invalid_tags = [tag for tag in tags if tag not in self.valid_tags]
        invalid_attrs = [attr for attr in attrs if attr not in self.valid_attrs]
        return (invalid_tags, invalid_attrs)

    def _cleanse_soup_tags(self, doc: str) -> str:
        pat = re.compile(r"<.*html>|<*.body>")
        doc = re.sub(pat, "", doc)
        return doc.strip()

    def cleanse_html(self, soup: BeautifulSoup) -> str:
        """Cleanse out the invalid_tags and invalid_attrs inside the html (BeautifulSoup object)."""

        invalid_tags, invalid_attrs = self._get_invalid_tags_attrs(soup)

        # remove invalid_tags
        for tag in invalid_tags:
            for match in soup.findAll(tag):
                match.unwrap()

        # remove invalid_attrs
        for tag in soup():
            for attr in invalid_attrs:
                del tag[attr]

        # remove empty tags
        for tag in soup.find_all():
            # As img tag generally has no content in it
            if tag.name != "img" and len(tag.get_text(strip=True)) == 0:
                tag.extract()

        doc = soup.prettify()
        doc = self._cleanse_soup_tags(doc)

        return doc
