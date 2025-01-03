import argparse

from aw_core.config import load_config_toml

default_config = """
[aw-watcher-screenshot]
exclude_title = false
exclude_titles = []
poll_time = 20.0
on_window_change = false
name_template = "monitor_{mon}_{date}.png"
strategy_macos = "swift"
""".strip()


def load_config():
    return load_config_toml("aw-watcher-screenshot", default_config)[
        "aw-watcher-screenshot"
    ]


def parse_args():
    config = load_config()

    default_poll_time = config["poll_time"]
    default_exclude_title = config["exclude_title"]
    default_exclude_titles = config["exclude_titles"]
    default_strategy_macos = config["strategy_macos"]
    default_on_window_change = config["on_window_change"]
    default_name_template = config["name_template"]

    parser = argparse.ArgumentParser(
        description="A cross platform window watcher for Activitywatch.\nSupported on: Linux (X11), macOS and Windows."
    )
    parser.add_argument("--host", dest="host")
    parser.add_argument("--port", dest="port")
    parser.add_argument("--testing", dest="testing", action="store_true")
    parser.add_argument(
        "--exclude-title",
        dest="exclude_title",
        action="store_true",
        default=default_exclude_title,
    )
    parser.add_argument(
        "--on_window_change",
        dest="on_window_change",
        action="store_true",
        default=default_on_window_change,
    )
    parser.add_argument(
        "--exclude-titles",
        dest="exclude_titles",
        nargs="+",
        default=default_exclude_titles,
        help="Exclude window titles by regular expression. Can specify multiple times.",
    )
    parser.add_argument("--verbose", dest="verbose", action="store_true")
    parser.add_argument(
        "--poll-time", dest="poll_time", type=float, default=default_poll_time
    )
    parser.add_argument(
        "--strategy",
        dest="strategy",
        default=default_strategy_macos,
        choices=["jxa", "applescript", "swift"],
        help="(macOS only) strategy to use for retrieving the active window.",
    )
    parser.add_argument(
        "--name_template",
        dest="name_template",
        default=default_name_template,
        help="Template for the screenshot filenames.",
    )
    parsed_args = parser.parse_args()
    return parsed_args
