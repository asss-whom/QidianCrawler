import atexit
import logging
import pickle
import random
import time

from dataclasses import dataclass
from os.path import exists

from DrissionPage import ChromiumOptions, ChromiumPage
from rich.logging import RichHandler
from rich.progress import Progress

log = logging.getLogger()


@dataclass
class Info:
    url: str
    name: str
    author: str
    urls: list[str]
    count: int  # 目前下载到的位置，用于断点续传。


class Crawler:
    def __init__(self, info: Info | None = None) -> None:
        self.info = info
        self.novel = []
        try:
            self.page = ChromiumPage()
        except FileNotFoundError:
            log.error("❗ Drissionself.Page没有找到Chrome浏览器")
            log.info("请按以下步骤操作：")
            log.info(
                "1. 打开浏览器，在地址栏输入chrome://version（Edge 输入edge://version），回车。"
            )
            log.info("2. 复制“可执行文件路径”后的值")
            log.info("3. 粘贴值至此处")
            path = input("值粘贴处：")
            ChromiumOptions().set_browser_path(path).set_retry(5, 5).save()
            self.page = ChromiumPage()

        log.info("🎉 DrissionPage 初始化成功")

    def get_index(self, url: str) -> Info:
        self.page.get(url)
        name = self.page.ele("#bookName").text
        author = self.page.ele(".author").text
        elems = self.page.s_eles(".chapter-name")
        urls = []
        for elem in elems:
            href = elem.attr("href")
            if href is not None:
                urls.append(href)
        return Info(url, name, author, urls, 0)  # type: ignore

    def get_chpt(self, chpt: str) -> str:
        self.page.get(chpt)
        content = []
        title = self.page.ele(".:title").text
        content.append(title)
        for elem in self.page.eles(".content-text"):
            content.append(elem.text)
        return "\n".join(content)

    def download(self, url: str) -> None:
        atexit.register(self.save)
        log.info(f"🎉 正在下载小说!")
        if self.info is not None:
            name, author, urls, count = (
                self.info.name,
                self.info.author,
                self.info.urls,
                self.info.count,
            )
            log.info("ℹ 已获取先前下载信息")
            log.info(f"《{name}》({author})， 已下载{count}章")
        else:
            index = self.get_index(url)
            self.info = index
            name, author, urls, count = (
                index.name,
                index.author,
                index.urls,
                index.count,
            )
            self.novel.append(name)
            self.novel.append(author)
        with Progress() as pg:
            download = pg.add_task("下载中", total=len(urls) - count)
            for i, url in enumerate(urls[count:]):
                chpt = self.get_chpt(url)
                self.novel.append(chpt)
                self.info.count = i + count
                pg.advance(download)
                time.sleep(random.randint(2, 5))

    def save(self) -> None:
        if self.info is None:
            return None
        name = self.info.name
        with open(f"{name}.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(self.novel))
            log.info("✨ 下载完毕")
        with open("temp.pkl", "wb") as f:
            pickle.dump(self.info, f)
            log.info("📕 下载信息已保存")


def main() -> None:
    url = input("请输入小说链接：")
    info = None
    if exists("temp.pkl"):
        with open("temp.pkl", "rb") as f:
            info = pickle.load(f)
    if isinstance(info, Info) and info.url == url:
        crawler = Crawler(info)
    else:
        crawler = Crawler()
    crawler.download(url)


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    log = logging.getLogger("rich")

    try:
        main()
    except Exception as e:
        log.exception(e)
