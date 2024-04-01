"""Module containing functionality related to unpacking a collection into a list of constituent
objects with metadata."""

import abc
import hashlib
import pathlib
import tarfile
import typing
import zipfile

import pydantic
import ssdeep

from gingko.server.extraction.model import Extraction, ExtractionType

UnpackedExtractionObjectType = typing.Literal["directory", "file"]


class UnpackedExtractionFileMetadata(typing.TypedDict):
    md5: str
    sha1: str
    ssdeep: str
    size: int


class UnpackedExtractionDirectoryMetadata(typing.TypedDict):
    ...


class UnpackedExtractionObject(pydantic.BaseModel):
    type: UnpackedExtractionObjectType
    path: pathlib.PurePath
    metadata: UnpackedExtractionFileMetadata | UnpackedExtractionDirectoryMetadata


class ExtractionUnpacker(abc.ABC):

    def generate_object_from_path(self, unpacked_object: pathlib.Path) -> UnpackedExtractionObject:
        if unpacked_object.is_dir():

            return UnpackedExtractionObject(
                type="directory", path=self._generate_extraction_reL_path(unpacked_object))

        else:

            file_content = unpacked_object.read_bytes()
            md5_hash = hashlib.md5(file_content).hexdigest()
            sha1_hash = hashlib.sha1(file_content).hexdigest()
            ssdeep_hash = ssdeep.hash(file_content)
            size = len(file_content)

            return UnpackedExtractionObject(
                type="file",
                path=self._generate_extraction_reL_path(unpacked_object),
                metadata={
                    "md5": md5_hash,
                    "sha1": sha1_hash,
                    "size": size,
                    "ssdeep": ssdeep_hash
                })

    @abc.abstractmethod
    def unpack_extraction(self, extraction: Extraction) -> UnpackedExtractionObject:
        ...


class DirectoryExtractionUnpacker(ExtractionUnpacker):

    def _generate_extraction_reL_path(extraction_path: pathlib.PurePath,
                                      object_path: pathlib.PurePath) -> pathlib.PurePath:
        return pathlib.Path("/") / object_path.relative_to(extraction_path)

    def unpack_extraction(self, extraction: Extraction) -> UnpackedExtractionObject:

        unpacked_extraction_objects: list[UnpackedExtractionObject] = []
        extraction_path = pathlib.Path(extraction.path)

        for unpacked_object in extraction_path.glob("**/*"):
            unpacked_extraction_objects.append(self.generate_object_from_path(unpacked_object))

        return unpacked_extraction_objects


class TarExtractionUnpacker(ExtractionUnpacker):

    def unpack_extraction(self, extraction: Extraction) -> UnpackedExtractionObject:

        extraction_tar = tarfile.open(extraction.path)

        members = extraction_tar.getmembers()

        unpacked_extraction_objects: list[UnpackedExtractionObject] = []

        for member in members:

            extraction_object: UnpackedExtractionObject | None = None

            if member.isfile():

                member_content = extraction_tar.extractfile(member).read()

                md5_hash = hashlib.md5(member_content).hexdigest()
                sha1_hash = hashlib.sha1(member_content).hexdigest()
                ssdeep_hash = ssdeep.hash(member_content)
                size = len(member_content)

                extraction_object = UnpackedExtractionObject(type="file",
                                                             path=member.path,
                                                             metadata={
                                                                 "md5": md5_hash,
                                                                 "sha1": sha1_hash,
                                                                 "size": size,
                                                                 "ssdeep": ssdeep_hash
                                                             })

            else:

                extraction_object = UnpackedExtractionObject(type="directory", path=member.path)

            unpacked_extraction_objects.append(extraction_object)

        return unpacked_extraction_objects


class ZipExtractionUnpacker(ExtractionUnpacker):

    def unpack_extraction(self, extraction: Extraction) -> UnpackedExtractionObject:

        extraction_zip = zipfile.ZipFile(extraction.path)

        members = extraction_zip.filelist

        unpacked_extraction_objects: list[UnpackedExtractionObject] = []

        for member in members:

            extraction_object: UnpackedExtractionObject | None = None

            if member.is_dir():

                extraction_object = UnpackedExtractionObject(type="directory", path=member.filename)

            else:

                member_content = extraction_zip.read(member)

                md5_hash = hashlib.md5(member_content).hexdigest()
                sha1_hash = hashlib.sha1(member_content).hexdigest()
                ssdeep_hash = ssdeep.hash(member_content)
                size = len(member_content)

                extraction_object = UnpackedExtractionObject(type="file",
                                                             path=member.path,
                                                             metadata={
                                                                 "md5": md5_hash,
                                                                 "sha1": sha1_hash,
                                                                 "size": size,
                                                                 "ssdeep": ssdeep_hash
                                                             })

            unpacked_extraction_objects.append(extraction_object)

        return unpacked_extraction_objects
