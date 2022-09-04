from brs import CONFIG_FILE_NAME, NoTitleException, ConfigLocationError
import requests
import os
import yaml
import csv
import click


def post_book(data, uri_base):
    if not data['title']:
        raise NoTitleException
    post_data = {
        'title'          : data['title'],
        'volume'         : data['volume']         or '',
        'series'         : data['series']         or '',
        'series_volume'  : data['series_volume']  or '',
        'author'         : data['author']         or '',
        'translator'     : data['translator']     or '',
        'publisher'      : data['publisher']      or '',
        'category'       : data['category']       or 'その他',
        'format'         : data['format']         or 'その他',
        'isbn'           : data['isbn']           or '',
        'published_on'   : data['published_on']   or '',
        'original_title' : data['original_title'] or '',
        'note'           : data['note']           or '',
        'keyword'        : data['keyword']        or '',
        'disk'           : data['disc']           or '',
        'disposed'       : '0'
    }
    uri = build_uri(uri_base, '/api/book/add/')
    res = requests.post(uri, json=post_data)
    return title_with_vol(res.json()['books'][0])


def title_with_vol(book):
    title = book['title']
    vol = book['volume']
    if vol:
        return f'{title} [{vol}]'
    else:
        return title


def load_yaml(yamlfile):
    if not os.path.exists(yamlfile):
        raise FileNotFoundError
    with open(yamlfile, 'r') as f:
        data = yaml.load(f)
    return data['books']


def load_csv(csvfile):
    if not os.path.exists(csvfile):
        raise FileNotFoundError
    data = []
    with open(csvfile, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def build_uri(repository, path, opts={}):
    if repository is None:
        raise click.BadParameter('--repository option is required.')
    uri = repository.rstrip('/') + path
    if opts:
        query = [ f'{key}={value}' for key, value in opts.items() ]
        uri = uri + '?' + '&'.join(query)
    return uri


def get_books(uri_base, limit, offset):
    uri = build_uri(uri_base, '/api/books/', {'limit': limit, 'offset': offset})
    res = requests.get(uri)
    return res.json()['books']


def load_config():
    try:
        config_file = config_file_location()
    except ConfigLocationError as e:
        print(e)
        exit(1)
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    return config


def save_config(config):
    with open(config_file_location(), 'w') as f:
        f.write(yaml.safe_dump(config, default_flow_style=False))


def config_file_location():
    try:
        if 'BRSCONFIG' in os.environ:
            return os.environ['BRSCONFIG']
        else:
            return os.path.join(os.environ['HOME'], CONFIG_FILE_NAME)
    except KeyError:
        raise ConfigLocationError
