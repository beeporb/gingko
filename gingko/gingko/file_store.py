"""Module containing functionality related to the Gingko File Store, which stores files once and
stores their metadata in Elastic."""

import abc
import hashlib
import pathlib
import shutil

import pydantic
import ssdeep

from gingko.errors import GingkoError


class GingkoFileStoreError(GingkoError):
    ...


class GingkoFileNotFound(GingkoFileStoreError):

    def __init__(self, file_hash: str) -> None:
        self.file_hash = file_hash

        super().__init__(f"File of hash {self.file_hash} not present in file-store.")


class GingkoFileDataComponent(abc.ABC):

    @abc.abstractmethod
    def store_file(self, file: pathlib.Path) -> str:
        ...

    @abc.abstractmethod
    def retrieve_file(self, **kwargs) -> pathlib.Path:
        ...


class GingkoFileMetadataComponent(abc.ABC):

    @abc.abstractmethod
    def store_file_metadata(self, file_metadata: dict) -> str:
        ...

    @abc.abstractmethod
    def retrieve_file_metadata(self, **kwargs) -> dict:
        ...


class GingkoFileStore:

    def __init__(self, data_component: GingkoFileDataComponent,
                 metadata_component: GingkoFileMetadataComponent) -> None:
        ...

    def store_file(self, file: pathlib.Path, file_metadata: dict) -> None:
        ...


class LocalFileDataStore(GingkoFileDataComponent):

    def __init__(self, file_store_root: pathlib.Path) -> None:
        self.file_store_root = file_store_root

    def _generate_sha1(self, file: pathlib.Path) -> str:
        return hashlib.sha1(file.read_bytes()).hexdigest()

    def _generate_file_path(self, file_hash: str) -> pathlib.Path:
        file_grandparent_dir = self.file_store_root / file_hash[:2]
        file_parent_dir = file_grandparent_dir / file_hash[2:4]
        file_parent_dir.mkdir(exist_ok=True, parents=True)
        return file_parent_dir / file_hash

    def store_file(self, file: pathlib.Path) -> str:
        file_hash = self._generate_sha1(file)
        stored_file_path = self._generate_file_path(file_hash)
        shutil.copy(file, stored_file_path)
        return stored_file_path

    def retrieve_file(self, file_hash: str) -> pathlib.Path:
        stored_file_path = self._generate_file_path(file_hash)

        if not stored_file_path.exists():
            raise GingkoFileNotFound(file_hash)

        return stored_file_path
