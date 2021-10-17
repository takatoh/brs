from brs import __version__, NoTitleException
from brs.functions import *
import sys
import click
import csv


def main():
    cmd(obj={})


@click.group()
@click.pass_context
@click.option('--repository', '-R', help='Specify repository.')
@click.version_option(version=__version__, message='v%(version)s')
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
    print('''---
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
    disc: ''')


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
