import logging
import pathlib
import tarfile
import time
import zipfile

from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent

from gingko.config import GINGKO_INPUT_DIR
from gingko.server.extraction.model import Extraction
from gingko.server.extraction.tracking import GingkoTrackingClient


class GingkoFileSystemEventHandler(FileSystemEventHandler):

    _VALID_FILE_EXTRACTION_EXTENSIONS: list[str] = [".tar", ".tar.gz", ".zip"]
    _FILE_EXTRACTION_EXTENSION_TO_EXTRACTION_TYPE_MAP = {
        ".tar": "tar",
        ".tar.gz": "tar",
        ".zip": "zip"
    }

    def __init__(self, gingko_tracking_client: GingkoTrackingClient) -> None:
        self.gingko_tracking_client = gingko_tracking_client

    def handle_zip_extraction_file(self, zip_extraction: pathlib.Path) -> Extraction:

        with zipfile.ZipFile(zip_extraction, "r") as z_fp:

            return Extraction(path=pathlib.PurePath(zip_extraction),
                              type="zip",
                              size_on_disk=zip_extraction.stat().st_size,
                              files=len(z_fp.filelist))

    def handle_tar_extraction_file(self, tar_extraction: pathlib.Path) -> Extraction:

        mode = "r:" if tar_extraction.suffix == ".tar" else "r:gz"

        with tarfile.open(str(tar_extraction), mode) as t_fp:

            return Extraction(path=pathlib.PurePath(tar_extraction),
                              type="tar",
                              size_on_disk=tar_extraction.stat().st_size,
                              files=len(t_fp.getmembers()))

    def handle_directory_extraction(self, directory_extraction: pathlib.Path) -> Extraction:

        files = len(list(directory_extraction.glob("**/*")))

        return Extraction(path=pathlib.PurePath(directory_extraction),
                          type="directory",
                          size_on_disk=directory_extraction.stat().st_size,
                          files=files)

    def handle_potential_extraction_file(self, event: FileCreatedEvent) -> None:
        event_file_path = pathlib.Path(event.src_path).resolve()

        if event_file_path.parent != GINGKO_INPUT_DIR:
            logging.info("skipping file %s as it looks like a component of an extraction directory",
                         event_file_path)
            return

        file_extension = "".join(event_file_path.suffixes)

        if file_extension not in self._VALID_FILE_EXTRACTION_EXTENSIONS:
            logging.info("skipping file %s as doesn't look like extraction (wrong file ext)",
                         event_file_path)
            return

        extraction_type = self._FILE_EXTRACTION_EXTENSION_TO_EXTRACTION_TYPE_MAP[file_extension]

        match extraction_type:

            case "tar":

                extraction = self.handle_tar_extraction_file(event_file_path)

            case "zip":

                extraction = self.handle_zip_extraction_file(event_file_path)

            case _:

                raise NotImplemented(
                    f"Extraction type {extraction_type} is bound but not implemented.")

        logging.info("picked up and adding tracking for new %s extraction: %s (%d files)",
                     extraction.type, extraction.path, extraction.files)

        self.gingko_tracking_client.add_tracking_for_extraction(extraction)

    def handle_potential_extraction_directory(self, event: DirCreatedEvent) -> None:
        event_directory_path = pathlib.Path(event.src_path).resolve()

        if event_directory_path.parent != GINGKO_INPUT_DIR:
            logging.info(
                "skipping directory %s as it looks like a component of a different directory "
                "extraction", event_directory_path)
            return

        extraction = self.handle_directory_extraction(event_directory_path)

        logging.info("picked up and adding tracking for new %s extraction: %s (%d files)",
                     extraction.type, extraction.path, extraction.files)

        self.gingko_tracking_client.add_tracking_for_extraction(extraction)

    def on_created(self, event: FileSystemEvent) -> None:
        if isinstance(event, FileCreatedEvent):
            self.handle_potential_extraction_file(event)
        elif isinstance(event, DirCreatedEvent):
            self.handle_potential_extraction_directory(event)


class GingkoDirectoryWatcher:

    def __init__(self, watch_dir: pathlib.Path,
                 gingko_tracking_client: GingkoTrackingClient) -> None:
        self.watch_dir = watch_dir
        self.gingko_tracking_client = gingko_tracking_client
        self.gingko_file_system_event_handler = GingkoFileSystemEventHandler(
            self.gingko_tracking_client)

        self.obs = Observer()
        self.obs.schedule(self.gingko_file_system_event_handler, self.watch_dir, recursive=True)

    def start(self) -> None:
        logging.info("starting extraction directory watcher (watching: %s)", self.watch_dir)

        self.obs.start()

        try:

            while True:

                time.sleep(1)

        finally:
            logging.info("gracefully stopping directory watcher...")
            self.obs.stop()
            self.obs.join()
