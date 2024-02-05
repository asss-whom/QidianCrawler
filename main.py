from logging import basicConfig, getLogger
from pathlib import Path
from random import randint, random
from time import sleep
from typing import Optional

from rich.logging import RichHandler
from rich.progress import Progress
from rich.prompt import Prompt
from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError

URL = str


class Qidian:
    def __init__(self) -> None:
        self.page = ChromiumPage()
        log.info("🎉 DrissionPage 初始化成功")

    def get_novel(self, url: URL) -> list[URL]:
        self.page.get(url)
        chpts = self.page.s_eles(".chapter-name")
        return list(filter(None, map(lambda chpt: chpt.attr("href"), chpts)))

    def download_novel(self, urls: list[URL], path: Path) -> None:
        log.info(f"🎉 正在下载小说!")
        novel = []

        with Progress() as pg:
            download = pg.add_task("[blue]下载中", total=len(urls))
            for url in urls:
                chpt = self._download_chpt(url)
                if chpt:
                    novel.append(chpt)
                    pg.update(download, advance=1)
                sleep(randint(5, 10) + random())
        log.info("✨ 下载完毕")
        path.write_text("\n".join(novel), encoding="utf-8")

    def _download_chpt(self, url: URL) -> Optional[str]:
        self.page.get(url)
        try:
            title = self.page.ele(".:title").text
            body = "\n".join(ele.text for ele in self.page.eles(".content-text"))  # type: ignore
            return f"{title}\n{body}\n"
        except ElementNotFoundError:
            log.warning("❗ 无法获取章节内容，已跳过此章节")


def main():
    url = Prompt.ask("请输入小说链接")
    qidian = Qidian()
    urls = qidian.get_novel(url)
    qidian.download_novel(urls, Path() / "novel.txt")


if __name__ == "__main__":
    basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    log = getLogger("rich")

    try:
        main()
    except Exception as e:
        log.exception(e)
