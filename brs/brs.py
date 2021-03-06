# encoding: utf-8


import sys
import os
import click
import yaml
import csv
import json
import requests


here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, '__init__.py')) as f:
    exec(f.read(), about)
VERSION = about['__version__']

CONFIG_FILE_NAME = '.brsconfig.yml'


class NoTitleException(Exception):
    def __str__(self):
        return 'No title found.'

class ConfigLocationError(Exception):
    def __str__(self):
        return 'No config file found or settled.'


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
    if book['volume']:
        return '{title} [{vol}]'.format(title=book['title'], vol=book['volume'])
    else:
        return book['title']

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
        query = []
        for k, v in opts.items():
            query.append('{key}={value}'.format(key=k, value=v))
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


@click.group()
@click.pass_context
@click.option('--repository', '-R', help='Specify repository.')
@click.version_option(version=VERSION, message='v%(version)s')
def cmd(ctx, repository):
    ctx.obj['repository'] = repository


@cmd.command(help='Post books to Bruschetta.')
@click.pass_context
@click.option('--csv', is_flag=True, help='Input from CSV.')
@click.argument('input')
def post(ctx, csv, input):
    try:
        if csv:
            books = load_csv(input)
        else:
            books = load_yaml(input)
    except FileNotFoundError as e:
        print('Error: File not found: {file}'.format(file=input))
        exit(1)
    if ctx.obj['repository']:
        repository = ctx.obj['repository']
    else:
        config = load_config()
        repository = config['repository']
    for book in books:
        try:
            print(post_book(book, repository))
        except NoTitleException as e:
            print('{0}: SKIP.'.format(e))


@cmd.command(help='Print YAML template to post.')
@click.pass_context
def template(ctx):
    print("""---
books:
  - title: 
    volume: 
    series: 
    series_volume: 
    author: 
    translator: 
    publisher: 
    category: 
    format: 
    isbn: 
    published_on: 
    original_title: 
    note: 
    keyword: 
    disc: """)


@cmd.command(help='Get book informations into CSV.')
@click.pass_context
@click.option('--limit', '-l', type=int, help='Limit of getting books.')
@click.option('--offset', '-o', type=int, help='Offset.')
@click.option('--all', '-a', is_flag=True, help='Dump all books.')
def csvdump(ctx, limit, offset, all):
    if ctx.obj['repository']:
        repository = ctx.obj['repository']
    else:
        config = load_config()
        repository = config['repository']
    if all:
        books = []
        limit = 100
        offset = 0
        while True:
            bks = get_books(repository, limit, offset)
            if not bks:
                break
            books.extend(bks)
            offset += limit
    else:
        books = get_books(repository, limit, offset)
    headers = [
        'title',
        'volume',
        'series',
        'series_volume',
        'author',
        'translator',
        'publisher',
        'category',
        'format',
        'isbn',
        'published_on',
        'original_title',
        'note',
        'keyword',
        'disc',
        'disposed'
    ]

    csvwriter = csv.writer(sys.stdout, lineterminator='\n')
    csvwriter.writerow(headers)
    for book in books:
        book_data = [
            book['title'],
            book['volume'],
            book['series'],
            book['series_volume'],
            book['author'],
            book['translator'],
            book['publisher'],
            book['category'],
            book['format'],
            book['isbn'],
            book['published_on'],
            book['original_title'],
            book['note'],
            book['keyword'],
            book['disk'],
        ]
        if book['disposed']:
            book_data.append('1')
        else:
            book_data.append('0')
        csvwriter.writerow(book_data)


@cmd.command(help='Get/set config.')
@click.pass_context
@click.option('--list', '-l', 'lst', is_flag=True, help='List config.')
@click.option('--delete', '-d', is_flag=True, help='Delete key and value from config.')
@click.argument('key', default='')
@click.argument('var', default='')
def config(ctx, key, var, lst, delete):
    config = load_config()
    if lst:
        for k, v in config.items():
            print('{key} = {value}'.format(key=k, value=v))
        exit()
    elif delete:
        if key in config:
            del config[key]
            save_config(config)
        exit()
    if var:
        config[key] = var
        save_config(config)
    else:
        if key in config:
            print(config[key])


def main():
    cmd(obj={})


if __name__ == '__main__':
    main()
