import asyncio
import logging
import threading
import socket
from shubcrawler.grabber import parse
from mitmproxy.http import HTTPFlow
from contextlib import closing
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster


class Sniffer:
    def __init__(self) -> None:
        self._logger = logging.getLogger("shubcrawler")
        self._logger.debug("Sniffer started.")

    def request(self, flow: HTTPFlow):
        headers = flow.request.headers
        self._logger.debug("Referer: {}".format(headers.get("Referer")))
        if not headers.get("Referer") == "https://shub.edu.vn/":
            return
        parse(flow.request)


class ProxyManager:
    def __init__(self):
        """
        Manage mitmproxy to create necessary proxy for the app to work.
        """
        self._mitm = None
        self._loop = self._create_loop()
        self.proxy_port = self._get_free_port()
        self._mitm_options = self._create_mitmproxy_options()
        self._logger = logging.getLogger("shub-file-grabber")

    @staticmethod
    def _get_free_port() -> int:
        """
        Get a free port to use with mitmproxy

        Source: https://stackoverflow.com/a/45690594/13671777

        :return: An integer representing the free port.
        """
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    @staticmethod
    def _create_loop():
        """
        Create a new event loop.
        :return: new event loop that is started and run forever.
        """
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever).start()
        return loop

    def _create_mitmproxy_options(self):
        """
        Create a new configuration for mitmproxy
        """
        options = Options(
            listen_host='127.0.0.1',
            listen_port=self.proxy_port
        )
        return options

    async def _create_mitmdump(self):
        # DumpMaster require an existing loop so we use async here.
        if self._mitm:
            self._logger.warning("mitmproxy is already created")
            return
        self._mitm = DumpMaster(options=self._mitm_options)
        self._mitm.addons.add(Sniffer())
        self._logger.debug("mitmproxy created")

    async def _run_mitmdump(self, port):
        if not self._mitm:
            await self._create_mitmdump()
        if port != 0:
            self.set_proxy_port(port)
        await self._mitm.run()

    def create_proxy(self):
        """
        It is optional to use this function unless you want to set mitmproxy port before starting proxy.
        :return:
        """
        asyncio.run_coroutine_threadsafe(self._create_mitmdump(), self._loop)

    def set_proxy_port(self, port: int):
        """
        Set the proxy port to the specified one.

        You must run create_proxy before this or it'll raise an error about mitmproxy doesn't exist.

        :param port: Port for the proxy to use, must be free.
        """
        if not self._mitm:
            self._logger.warning("mitmproxy hasn't been created yet.")
            raise RuntimeError("mitmproxy doesn't exist.")
        self._mitm.options.update(listen_port=port)

    def start_proxy(self, port: int = 0):
        """
        Start mitmproxy.

        :return: None if everything succeeded.
        """
        asyncio.run_coroutine_threadsafe(self._run_mitmdump(port), self._loop)

    def stop_proxy(self):
        if not self._mitm:
            logging.warning("mitmproxy hasn't been created yet.")
            return
        self._mitm.shutdown()
        del self._mitm
        self._loop.stop()
