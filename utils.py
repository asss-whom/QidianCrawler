import logging

from typing import NamedTuple

from DrissionPage import ChromiumPage
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
)
log = logging.getLogger("rich")


class Index(NamedTuple):
    name: str
    urls: list[str]


class Crawler:
    def __init__(self) -> None:
        self.page = ChromiumPage()
        log.info("🎉 DrissionPage 初始化成功")

    def get_index(self, url: str) -> Index:
        self.page.get(url)
        name = self.page.ele("#bookName").text
        elems = self.page.s_eles(".chapter-name")
        urls = []
        for elem in elems:
            href = elem.attr("href")
            if href is not None:
                urls.append(href)
        return Index(name, urls)  # type: ignore

    def get_chpt(self, chpt: str) -> str:
        self.page.get(chpt)
        content = []
        title = self.page.ele(".:title").text
        content.append(title)
        for elem in self.page.eles(".content-text"):
            content.append(elem.text)
        return "\n".join(content)
