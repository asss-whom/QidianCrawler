import argparse
import random
import time
from pathlib import Path

from rich.progress import Progress

from utils import Crawler, log


def main() -> None:
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
    args = parser.parse_args()

    if args.mode == "full":
        full_download(args.url)
    else:
        if args.upper_bound is None or args.lower_bound is None:
            parser.error("在范围模式下，必须同时提供 --upper-bound 和 --lower-bound")
        range_donwload(args.url, args.lower_bound, args.upper_bound)


def save(name: str, content: str) -> None:
    path = Path(f"{name}.txt")
    path.write_text(content, "utf-8")


def full_download(url: str) -> None:
    crawler = Crawler()
    log.info("🎉 DrissionPage初始化完毕")

    index = crawler.get_index(url)
    log.info(f"🎈 正在下载《{index.name}》，具有{len(index.chpts)}章节的小说")

    chpts: list[str] = []
    with Progress() as progress:
        download = progress.add_task("🛻 下载中", total=len(index.chpts))
        try:
            for info in index.chpts:
                chpt = crawler.get_chpt(info.url)
                chpts.append(chpt)
                progress.advance(download)
                time.sleep(random.randint(5, 7))
        except Exception as e:
            log.error(e)
        finally:
            content = "\n".join(chpts)
            save(index.name, content)
            log.info("✨ 小说保存完毕")


def range_donwload(url: str, lower_bound: int, upper_bound: int) -> None:
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    lower_bound -= 1  # 更加符合习惯用法

    crawler = Crawler()
    log.info("🎉 DrissionPage初始化完毕")

    index = crawler.get_index(url)
    lower_name = index.chpts[lower_bound].name
    upper_name = index.chpts[upper_bound - 1].name
    log.info(f"🎈 正在下载《{index.name}》，范围从《{lower_name}》到《{upper_name}》")

    chpts: list[str] = []
    with Progress() as progress:
        download = progress.add_task("🛻 下载中", total=upper_bound - lower_bound)
        try:
            for info in index.chpts[lower_bound:upper_bound]:
                chpt = crawler.get_chpt(info.url)
                chpts.append(chpt)
                progress.advance(download)
                time.sleep(random.randint(5, 7))
        except Exception as e:
            log.error(e)
        finally:
            content = "\n".join(chpts)
            save(f"{index.name}-{lower_bound + 1}-{upper_bound}", content)
            log.info("✨ 小说保存完毕")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(e)
