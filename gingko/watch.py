from gingko.config import GINGKO_INPUT_DIR
from gingko.log import init_logger
from gingko.server.extraction.tracking import RedisGingkoTrackingClient
from gingko.watcher import GingkoDirectoryWatcher


def main() -> None:
    init_logger()
    gingko_directory_watcher = GingkoDirectoryWatcher(GINGKO_INPUT_DIR, RedisGingkoTrackingClient())
    gingko_directory_watcher.start()


if __name__ == "__main__":
    main()
