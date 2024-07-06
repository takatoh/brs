from brs import __version__, NoTitleException
from brs import functions as func
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
@click.option('--ignore-notitle', is_flag=True, help='Ignore data has no title.')
@click.argument('input')
def post(ctx, csv, ignore_notitle, input):
    try:
        if csv:
            books = func.load_csv(input)
        else:
            books = func.load_yaml(input)
    except FileNotFoundError:
        print(f'Error: File not found: {input}')
        exit(1)
    if ctx.obj['repository']:
        repository = ctx.obj['repository']
    else:
        config = func.load_config()
        repository = config['repository']
    for book in books:
        try:
            print(func.post_book(book, repository))
        except NoTitleException as e:
            if not ignore_notitle:
                print(f'{str(e)}: SKIP.')


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
    disc: 
    bookshelf: ''')


@cmd.command(help='Get book informations into CSV.')
@click.pass_context
@click.option('--limit', '-l', type=int, help='Limit of getting books.')
@click.option('--offset', '-o', type=int, help='Offset.')
@click.option('--all', '-a', is_flag=True, help='Dump all books.')
@click.option('--output', '-O', help='Specify output file.')
def csvdump(ctx, limit, offset, all, output):
    if ctx.obj['repository']:
        repository = ctx.obj['repository']
    else:
        config = func.load_config()
        repository = config['repository']
    if all:
        books = []
        limit = 100
        offset = 0
        while True:
            bks = func.get_books(repository, limit, offset)
            if not bks:
                break
            books.extend(bks)
            offset += limit
    else:
        books = func.get_books(repository, limit, offset)
    headers = [
        'id',
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
        'bookshelf',
        'disposed'
    ]

    if output:
        output_file = open(output, 'w', encoding='utf-8')
        csvwriter = csv.writer(output_file, lineterminator='\n')
    else:
        csvwriter = csv.writer(sys.stdout, lineterminator='\n')
    csvwriter.writerow(headers)
    for book in books:
        book_data = [
            book['id'],
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
            book['bookshelf'],
        ]
        if book['disposed']:
            book_data.append('1')
        else:
            book_data.append('0')
        csvwriter.writerow(book_data)
    if output:
        output_file.close()


@cmd.command(help='Get/set config.')
@click.pass_context
@click.option('--list', '-l', 'lst', is_flag=True, help='List config.')
@click.option('--delete', '-d', is_flag=True, help='Delete key and value from config.')
@click.argument('key', default='')
@click.argument('val', default='')
def config(ctx, key, val, lst, delete):
    config = func.load_config()
    if lst:
        for key, value in config.items():
            print(f'{key} = {value}')
        exit()
    elif delete:
        if key in config:
            del config[key]
            func.save_config(config)
        exit()
    if val:
        config[key] = val
        func.save_config(config)
    else:
        if key in config:
            print(config[key])
