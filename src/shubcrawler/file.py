import mimetypes
import time
from urllib.parse import urlparse, unquote
from pathlib import PurePath
from datetime import datetime


class File:
    def __init__(self, url: str, content_type: str = None, source: str = None, source_host: str = None):
        """
        A file got from the grabber.

        Do not initialize this class manually, this class is automatically created by the crawler
        when it found a file.

        :param url: File url
        :param content_type: mimetype, if not specified then this will get the mimetype from file
        name using mimetypes.guess_type
        """
        self._url = url
        self._source = source
        self._source_host = source_host
        if not content_type:
            content_type = mimetypes.guess_type(url)[0]
        self._content_type = content_type
        self._crawled_time = time.time()
        # Do some work here
        file_name = PurePath(unquote(urlparse(url).path)).name
        # File name format: <unix timestamp in milliseconds>_<file_name>.<format>
        # And no, you can't reverse to get actual file name.
        self._unix_time = float(file_name.split("_")[0]) / 1000
        self._time = datetime.fromtimestamp(self._unix_time)
        self._utc_time = datetime.utcfromtimestamp(self._unix_time)

    @property
    def url(self) -> str:
        return self._url

    @property
    def source(self) -> str:
        return self._source

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def crawled_time(self) -> float:
        return self._crawled_time

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def utc_time(self) -> datetime:
        return self._utc_time

    @property
    def unix_time(self) -> float:
        return self._unix_time

    @property
    def source_host(self):
        return self._content_type

    def __eq__(self, other):
        return self._url == other.url
