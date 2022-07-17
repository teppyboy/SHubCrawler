mkdir build/win/
cd build/win/
py -m nuitka --standalone --enable-plugin=pyside6,upx --follow-imports --nofollow-import-to=PyQt5 --include-module=shubcrawler,passlib.handlers --include-package-data=shubcrawler-gui,mitmproxy ../../src/shubcrawler-gui
