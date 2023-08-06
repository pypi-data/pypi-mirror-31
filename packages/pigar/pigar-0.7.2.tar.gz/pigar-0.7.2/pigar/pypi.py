# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import gzip
import json
import collections
try:  # py2
    from urllib2 import urlopen, Request
    from HTMLParser import HTMLParser
    from urlparse import urljoin
except ImportError:  # py3
    from urllib.request import urlopen, Request
    from html.parser import HTMLParser
    from urllib.parse import urljoin


from .db import database
from .unpack import top_level, try_unpack_resp
from .log import logger
from .utils import Color, compare_version, cmp_to_key
from .extractor import Extractor


PYPI_URL = 'https://pypi.org'
PKG_URL = urljoin(PYPI_URL, '/pypi/{0}')
PKGS_URL = urljoin(PYPI_URL, '/simple/')
PKG_INFO_URL = urljoin(PYPI_URL, '/pypi/{0}/json')
ACCEPTABLE_EXT = ('.whl', '.egg', '.tar.gz', '.tar.bz2', '.zip')


def search_names(names, installed_pkgs):
    """Search package information by names(`import XXX`).
    """
    results = collections.defaultdict(list)
    not_found = list()
    for name in names:
        logger.info('Searching package name for "{0}" ...'.format(name))
        # If exists in local environment, do not check on the PyPI.
        if name in installed_pkgs:
            results[name].append(list(installed_pkgs[name]) + ['local'])
        # Check information on the PyPI.
        else:
            rows = None
            with database() as db:
                rows = db.query_all(name)
            if rows:
                for row in rows:
                    version = extract_pkg_version(row.package)
                    results[name].append((row.package, version, 'PyPI'))
            else:
                not_found.append(name)
    return results, not_found


def check_latest_version(package):
    """Check package latest version in PyPI."""
    version = extract_pkg_version(package)
    return version


def update_db():
    """Update database."""
    print(Color.BLUE('Starting update database (this will take a while)...'))
    logger.info('Crawling "{0}" ...'.format(PKGS_URL))
    try:
        data = download(PKGS_URL)
    except Exception:
        logger.error("Fetch all packages got: ", exc_info=True)
        print(Color.RED('Operation abort ...'))
        return

    logger.info('Extracting all packages ...')
    pkg_names = _extract_html(data)
    with database() as db:
        ignore_pkgs = db.query_package(None)
        pkg_names = list(set(pkg_names) - set(ignore_pkgs))
    extractor = Extractor(pkg_names)
    extractor.run(extract_pkg_info)
    print(Color.BLUE('Operation done!'))


def extract_pkg_info(pkg_name):
    """Extract package information from PyPI."""
    logger.info('Extracting information of package "{0}".'.format(pkg_name))
    data = _pkg_json_info(pkg_name)
    # Extracting names which can be imported.
    if not data or not data['urls']:
        logger.warning('Package "{0}" no longer available.'.format(pkg_name))
        return

    urls = [item['url'] for item in data['urls']
            if item['filename'].endswith(ACCEPTABLE_EXT)]
    # Has not satisfied compressed package.
    if not urls:
        logger.warning('Package "{0}" can not unpack.'.format(pkg_name))
        return
    url = urls[0]

    top_levels = top_level(url, download(url))
    # Maybe package is a project, not importable...
    if not top_levels:
        logger.warning(
            'Maybe package "{0}" is not importable.'.format(pkg_name))
        return

    # Insert into database.
    with database() as db:
        db.insert_package(pkg_name)
        package = db.query_package(pkg_name)
        for top in top_levels:
            top = top or pkg_name  # empty top_level.txt
            db.insert_name(top, package.id)


def extract_pkg_version(pkg_name):
    """Extract package latest version from PyPI."""
    data = _pkg_json_info(pkg_name)
    if not data or not data['releases'] or not data['urls']:
        return 'unknown'
    latest = data['info'].get('version', None)
    if latest is None:
        latest = sorted(data['releases'], key=cmp_to_key(compare_version))
        latest = latest[-1]
    return latest


def _pkg_json_info(pkg_name):
    data = download(PKG_INFO_URL.format(pkg_name))
    if not data:  # 404
        return None
    data = json.loads(data)
    return data


# Fake headers, just in case.
_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64; rv:13.0) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/44.0.2403.157 Safari/537.36'),
}


def download(url, headers=_HEADERS):
    """Download data from url."""
    resp = urlopen(Request(url, headers=headers))
    try:
        return try_unpack_resp(resp)
    finally:
        resp.close()


def _extract_html(html):
    """Extract data from html."""
    names = list()

    class HrefParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                attrs = dict(attrs)
                if attrs.get('href', None):
                    names.append(attrs['href'])

    HrefParser().feed(html)
    return names
