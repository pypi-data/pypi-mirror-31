from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)

import datetime
import os
import re
import json
from urllib.parse import urljoin, urlsplit

from lxml import etree

import pandas as pd

import requests as r


def datetime_to_string(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def unix_time_millis(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000)


def get_instrument_df(epochsec):
    req_inst = r.get('http://ooi.visualocean.net/instruments.json',
                     params={'_': epochsec})
    df = pd.DataFrame.from_records(req_inst.json()['data'])
    df.loc[:, 'status'] = df.apply(lambda x: x.status.split(' ')[-1:][0], axis=1)

    return df


def get_science_data_stream_meta(reference_designator, region):
    # For both science and engineering: 'http://ooi.visualocean.net/data-streams/export'
    url = 'http://ooi.visualocean.net/data-streams/science/'
    dsdf = pd.read_csv(os.path.join(url, region))

    return dsdf


def get_nc_urls(thredds_url):
    caturl = thredds_url.replace('.html', '.xml')

    parsed_uri = urlsplit(caturl)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    response = r.get(caturl)
    ROOT = etree.XML(response.content)
    dataset_el = list(filter(lambda x: re.match(r'(.*?.nc$)', x.attrib['urlPath']) is not None,
                             ROOT.xpath('//*[contains(@urlPath, ".nc")]')))

    service_el = ROOT.xpath('//*[contains(@name, "odap")]')[0]

    dataset_urls = [urljoin(domain, urljoin(service_el.attrib['base'], el.attrib['urlPath'])) for el in
                    dataset_el]  # noqa

    return dataset_urls


def set_credentials_file(username=None, token=None):
    netrc_template = """machine ooinet.oceanobservatories.org
                        login {username}
                        password {token}""".format
    home_dir = os.environ.get('HOME')

    if username and token:
        fpath = os.path.join(home_dir, '.netrc')
        with open(fpath, 'w') as f:
            f.write(netrc_template(username=username,
                                   token=token))
        os.chmod(fpath, 0o700)
    else:
        raise EnvironmentError('Please enter your ooinet username and token!')
