import logging
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
from time import sleep

from aw_client import ActivityWatchClient
from aw_core.log import setup_logging
from aw_core.models import Event
from aw_core.dirs import ensure_path_exists, get_data_dir

from aw_watcher_screenshot.config import parse_args
from aw_watcher_window.exceptions import FatalError
from aw_watcher_window.lib import get_current_window
from aw_watcher_window.macos_permissions import background_ensure_permissions

import mss


logger = logging.getLogger(__name__)

# run with LOG_LEVEL=DEBUG
log_level = os.environ.get("LOG_LEVEL")
if log_level:
    logger.setLevel(logging.__getattribute__(log_level.upper()))


def kill_process(pid):
    logger.info("Killing process {}".format(pid))
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        logger.info("Process {} already dead".format(pid))


def try_compile_title_regex(title):
    try:
        return re.compile(title, re.IGNORECASE)
    except re.error:
        logger.error(f"Invalid regex pattern: {title}")
        exit(1)


def main():
    args = parse_args()
    print(args)

    if sys.platform.startswith("linux") and (
        "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
    ):
        raise Exception("DISPLAY environment variable not set")

    setup_logging(
        name="aw-watcher-screenshot",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    if sys.platform == "darwin":
        background_ensure_permissions()

    client = ActivityWatchClient(
        "aw-watcher-screenshot", host=args.host, port=args.port, testing=args.testing
    )

    bucket_id = f"{client.client_name}_{client.client_hostname}"
    event_type = "screenshot"

    client.create_bucket(bucket_id, event_type, queued=True)

    logger.info("aw-watcher-screenshot started")
    client.wait_for_start()

    if args.on_window_change:
        raise NotImplementedError("on_monitor_change is not implemented yet")

    storage_path = os.path.join(get_data_dir("aw-watcher-screenshot"), "screenshots")
    ensure_path_exists(storage_path)

    with client:
        if sys.platform == "darwin" and args.strategy == "swift":
            logger.info("Using swift strategy, calling out to swift binary")
            binpath = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "aw-watcher-window-macos"
            )

            try:
                p = subprocess.Popen(
                    [
                        binpath,
                        client.server_address,
                        bucket_id,
                        client.client_hostname,
                        client.client_name,
                    ]
                )
                # terminate swift process when this process dies
                signal.signal(signal.SIGTERM, lambda *_: kill_process(p.pid))
                p.wait()
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                kill_process(p.pid)
        else:
            heartbeat_loop(
                client,
                bucket_id,
                poll_time=args.poll_time,
                strategy=args.strategy,
                name_template=args.name_template,
                storage_path=storage_path,
                exclude_title=args.exclude_title,
                exclude_titles=[
                    try_compile_title_regex(title)
                    for title in args.exclude_titles
                    if title is not None
                ],
            )


def screenshot(name_template: str) -> str:
    formatted_date = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    f_name = name_template.replace("{date}", formatted_date)
    with mss.mss(compression_level=6) as sct:
        screenshot = sct.shot(output=f_name)
    return screenshot


def heartbeat_loop(
    client,
    bucket_id,
    poll_time,
    strategy,
    name_template,
    storage_path,
    exclude_title=False,
    exclude_titles=[],
):
    while True:
        if os.getppid() == 1:
            logger.info("window-watcher stopped because parent process died")
            break

        current_window = None
        try:
            current_window = get_current_window(strategy)
            logger.debug(current_window)
        except (FatalError, OSError):
            # Fatal exceptions should quit the program
            try:
                logger.exception("Fatal error, stopping")
            except OSError:
                pass
            break
        except Exception:
            # Non-fatal exceptions should be logged
            try:
                # If stdout has been closed, this exception-print can cause (I think)
                #   OSError: [Errno 5] Input/output error
                # See: https://github.com/ActivityWatch/activitywatch/issues/756#issue-1296352264
                #
                # However, I'm unable to reproduce the OSError in a test (where I close stdout before logging),
                # so I'm in uncharted waters here... but this solution should work.
                logger.exception("Exception thrown while trying to get active window")
            except OSError:
                break

        if current_window is None:
            logger.debug("Unable to fetch window, trying again on next poll")
        else:
            for pattern in exclude_titles:
                if pattern.search(current_window["title"]):
                    current_window["title"] = "excluded"

            if exclude_title:
                current_window["title"] = "excluded"

            screenshot_path = screenshot(os.path.join(storage_path, name_template))

            relative_screenshot_path = "/{}/{}".format(
                os.path.basename(os.path.dirname(screenshot_path)),
                os.path.basename(screenshot_path),
            )

            logger.debug(f"Screenshot saved to: {screenshot_path}")

            current_window["screenshot"] = relative_screenshot_path
            now = datetime.now(timezone.utc)
            current_window_event = Event(timestamp=now, duration=5, data=current_window)

            # Set pulsetime to 1 second more than the poll_time
            # This since the loop takes more time than poll_time
            # due to sleep(poll_time).
            client.heartbeat(
                bucket_id, current_window_event, pulsetime=poll_time + 1.0, queued=True
            )

        sleep(poll_time)


if __name__ == "__main__":
    main()
