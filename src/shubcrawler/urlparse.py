import logging
from urllib.parse import urlparse, parse_qs

_logger = logging.getLogger("shubcrawler")


class UrlParse:
    def __init__(self):
        """
        This is an Url parser to get Shub document embedded in the Url params.
        """
        pass

    @staticmethod
    def _get_query(url: str):
        """
        Not used for now
        :param url: File url
        :return:
        """
        return parse_qs(urlparse(url).query)

    @staticmethod
    def shub_storage(url_str: str) -> str | None:
        """
        Parse a shub-storage.sgp1.cdn.digitaloceanspaces.com url

        :param url_str: The url (must be the host above with /user_files/ or /tests/ in path)

        :return: The url if it's a valid file url, otherwise `None`
        """
        url = urlparse(url_str)
        if url.hostname != "shub-storage.sgp1.cdn.digitaloceanspaces.com":
            return
        if not url.path.startswith(("/user_files/", "/tests/")):
            return
        return url_str

    @staticmethod
    def google_drive(url_str: str) -> str | None:
        """
        Parse a drive.google.com url

        :param url_str: The url (must be the host above with /viewerng/viewer in path)

        :return: The url if it's a valid file url, otherwise `None`
        """
        _logger.debug("Using Google Drive viewerng parser.")
        url = urlparse(url_str)
        if url.hostname != "drive.google.com":
            return
        if not url.path.startswith("/viewerng/viewer"):
            return
        query = parse_qs(url.query)
        # Google Drive query:
        # {'url': ['<url>'], 'embedded': ['true'], 'hl': ['en']}
        return query["url"][0]

    @staticmethod
    def office_online(url_str: str) -> str | None:
        """
        Parse a view.officeapps.live.com url

        :param url_str: The url (must be the host above with /op/embed.aspx in path)

        :return: The url if it's a valid file url, otherwise `None`
        """
        _logger.debug("Using Office online embed parser.")
        url = urlparse(url_str)
        if url.hostname != "view.officeapps.live.com":
            return
        if not url.path.startswith("/op/embed.aspx"):
            return
        query = parse_qs(url.query)
        # Office query:
        # {'src': ['<url>']}
        return query["src"][0]
