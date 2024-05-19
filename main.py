import atexit
import argparse
import functools
import random
import time

from dataclasses import dataclass
from typing import Any

from rich.progress import Progress

from utils import *


@dataclass
class FullInfo:
    name: str
    total: int
    chpts: list[str]

    @property
    def is_finished(self) -> bool:
        return len(self.chpts) == self.total

    @property
    def progress(self) -> int:
        return len(self.chpts)


@dataclass
class RangeInfo:
    name: str
    lower_bound: int
    upper_bound: int
    chpts: list[str]

    @property
    def is_finished(self) -> bool:
        return len(self.chpts) == self.upper_bound - self.lower_bound

    @property
    def progress(self) -> int:
        return self.lower_bound + len(self.chpts)


def create_parser():
    parser = argparse.ArgumentParser(description="🕸️ 基于DrissionPage库的起点小说爬虫。")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["full", "range"],
        required=True,
        help='下载模式：选择 "full" 为全文下载，选择 "range" 为范围下载',
    )
    parser.add_argument("url", type=str, help="目录页的URL")

    # 这些参数仅在'range'模式下需要
    parser.add_argument(
        "-u",
        "--upper-bound",
        type=int,
        default=None,
        help='范围下载的上界（仅当选择 "range" 模式时有效）',
    )
    parser.add_argument(
        "-l",
        "--lower-bound",
        type=int,
        default=None,
        help='范围下载的下界（仅当选择 "range" 模式时有效）',
    )

    return parser


def download_range_content(url: str, lower_bound: int, upper_bound: int) -> None:
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    lower_bound -= 1  # 更加符合习惯用法

    crawler = Crawler()
    index = crawler.get_index(url)
    info = RangeInfo(index.name, lower_bound, upper_bound, [])
    atexit.register(save, info)

    with Progress() as progress:
        download = progress.add_task("🚚 下载中", total=upper_bound - lower_bound)
        for url in index.urls[lower_bound:upper_bound]:
            chpt = crawler.get_chpt(url)
            info.chpts.append(chpt)
            progress.advance(download)
            time.sleep(random.randint(5, 9) + random.random())


def download_full_content(url: str) -> None:
    crawler = Crawler()
    index = crawler.get_index(url)
    info = FullInfo(index.name, len(index.urls), [])
    atexit.register(save, info)

    with Progress() as progress:
        download = progress.add_task("🚚 下载中", total=len(index.urls))
        for url in index.urls:
            chpt = crawler.get_chpt(url)
            info.chpts.append(chpt)
            progress.advance(download)
            time.sleep(random.randint(5, 9) + random.random())


@functools.singledispatch
def save(info: Any) -> None:
    raise RuntimeError("Unreachable!")


@save.register
def _(info: FullInfo) -> None:
    if info.is_finished:
        log.info("✨ 小说下载成功")
    else:
        log.warning("❗ 小说下载未完成")
        log.info(f"📌 已下载至{info.progress}章")

    with open(f"{info.name}-full.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(info.chpts))
    log.info("✨ 小说保存成功")


@save.register
def _(info: RangeInfo) -> None:
    if info.is_finished:
        log.info("✨ 小说分章节下载成功")
    else:
        log.warning("❗ 小说下载未完成")
        log.info(f"📌 已下载至{info.progress}章")

    with open(
        f"{info.name}-{info.lower_bound}-{info.progress}.txt", "w", encoding="utf-8"
    ) as f:
        f.write("\n".join(info.chpts))
    log.info("✨ 小说分章节保存成功")


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.mode == "full":
        log.info(f"🎉 正在从URL下载全文内容：{args.url}")
        # 调用下载全文的函数
        download_full_content(args.url)
    elif args.mode == "range":
        if args.upper_bound is None or args.lower_bound is None:
            parser.error("在范围模式下，必须同时提供 --upper-bound 和 --lower-bound")
        log.info(
            f"🎉 正在从URL下载内容：{args.url}，范围从 {args.lower_bound} 到 {args.upper_bound}"
        )
        # 调用下载指定范围的函数
        download_range_content(args.url, args.lower_bound, args.upper_bound)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(e)
