import logging

from urllib.parse import urlparse
from mitmproxy.http import Request
from shubcrawler.file import File
from shubcrawler.urlparse import UrlParse

_callbacks = []
_files = []
_logger = logging.getLogger("shubcrawler")


@property
def callbacks():
    return _callbacks


def add_callback(callback):
    _callbacks.append(callback)


def remove_callback(callback):
    _callbacks.remove(callback)


def _add_file(file: File):
    _files.append(file)


@property
def files():
    return _files


def _fire_callbacks(*args, **kwargs):
    for cb in _callbacks:
        cb(*args, **kwargs)


def parse(request: Request):
    url = request.url
    # Hacky way to fake our "authority"
    authority = request.authority if request.authority != "" else urlparse(url).hostname
    file = None
    _logger.debug("Processing authority: {} (real authority: {})".format(authority, request.authority))

    # Parse happens here
    try:
        match authority:
            case "drive.google.com":  # Google Drive
                file = File(url=UrlParse.google_drive(url), source="google-drive", source_host=authority)
                _logger.debug("Got a Google Drive document URL: {}".format(file.url))
            case "view.officeapps.live.com":  # Office
                file = File(url=UrlParse.office_online(url), source="office-online", source_host=authority)
                _logger.debug("Got an Office online document URL: {}".format(file.url))
            case "shub-storage.sgp1.cdn.digitaloceanspaces.com":    # SHub storage
                file = File(url=UrlParse.shub_storage(url), source="shub-storage", source_host=authority)
                _logger.debug("Got a SHub storage document URL: {}".format(file.url))

    except TypeError:
        return

    if file is None:
        return

    _add_file(file)
    _fire_callbacks(file=file)
