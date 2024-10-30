from typing import List, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from splitter.constant import DEFAULT_VALID_ATTRS, DEFAULT_VALID_TAGS
from splitter.logger import set_logger

set_logger(source="cleanser", diagnose=False, to_file=False)


class HTMLCleanser(object):
    """Cleanser to cleanse out the invalid tags or attributes
    except the valid ones inside the html.

    Example:
        .. code-block:: python

            from bs4 import BeautifulSoup
            from _html.cleanser import HTMLCleanser

            soup = BeautifulSoup("YOUR_HTML", "lxml")
            cleanser = HTMLCleanser()

            # add or remove any tag as your pleases.
            cleanser.add_valid_tags(["p", "img", "a", "span", "title"])
            cleanser.remove_valid_tags(["span"])

            # add or remove any attributes as your pleases.
            cleanser.add_valid_attrs(["href", "src", "alt", "font"])
            cleanser.remove_valid_attrs(["font"])

            # cleanse the html
            soup = cleanser.cleanse_html(soup)
    """

    def __init__(self, valid_tags: List[str] = None, valid_attrs: List[str] = None):
        # initialize valid_tags and valid_attrs
        self.__valid_tags = DEFAULT_VALID_TAGS if valid_tags is None else valid_tags
        self.__valid_attrs = DEFAULT_VALID_ATTRS if valid_attrs is None else valid_attrs

        logger.info(
            f"""No valid_tags or valid_attrs provided.
                    Initialize the HTMLCleanser with default ones:
                    - valid_tags: {self.valid_tags}
                    - valid_attrs: {self.valid_attrs}"""
        )

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

    def add_valid_tags(self, tags: List[str]) -> None:
        tag_sets = set(self.valid_tags)
        tag_sets.update(tags)
        self.valid_tags = list(tag_sets)
        logger.info(f"valid_tags: {self.valid_tags}")

    def add_valid_attrs(self, attrs: List[str]) -> None:
        attr_sets = set(self.valid_attrs)
        attr_sets.update(attrs)
        self.valid_attrs = list(attr_sets)
        logger.info(f"valid_attrs: {self.valid_attrs}")

    def remove_valid_tags(self, tags: List[str]) -> None:
        self.valid_tags = [tag for tag in self.valid_tags if tag not in tags]
        logger.info(f"valid_tags: {self.valid_tags}")

    def remove_valid_attrs(self, attrs: List[str]) -> None:
        self.valid_attrs = [attr for attr in self.valid_attrs if attr not in attrs]
        logger.info(f"valid_attrs: {self.valid_attrs}")

    def _get_invalid_tags_attrs(self, soup: BeautifulSoup) -> Tuple[list, list]:
        """Get invalid tags and attributes to remove in html.
        It's used in the `cleanse_html` internally."""
        tags, attrs = set(), set()
        for tag in soup.find_all():
            tags.add(tag.name)
            attrs.update(list(tag.attrs.keys()))

        invalid_tags = [tag for tag in tags if tag not in self.valid_tags]
        invalid_attrs = [attr for attr in attrs if attr not in self.valid_attrs]
        return (invalid_tags, invalid_attrs)

    def cleanse_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Cleanse out the invalid_tags and invalid_attrs inside the BeautifulSoup object.

        Args:
            soup: BeautifulSoup object

        Returns:
            cleansed soup object

        Example:
            .. code-block:: python
            txt="YOUR_HTML"
            soup = BeautifulSoup(soup, 'lxml')
            cleanser = HTMLCleanser()
            soup = cleanser.cleanse_html(soup)
        """
        # get invalid tags and attributes
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
            # img tag generally has no content in it.
            if tag.name != "img" and len(tag.get_text(strip=True)) == 0:
                tag.extract()

        return soup
