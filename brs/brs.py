#!/usr/bin/env python
# encoding: utf-8


import sys
import click
import yaml
import csv
import json
import requests


script_version = '0.2.0'


def post_book(data, uri_base):
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
        'disk'           : data['disk']           or '',
        'disposed'       : data['disposed']       or '0'
    }
    uri = build_uri(uri_base, '/api/book/add/')
    res = requests.post(uri, json=post_data)
    return title_with_vol(res.json()['books'][0])

def title_with_vol(book):
    if book['volume']:
        return book['title'] + ' [' + book['volume'] + ']'
    else:
        return book['title']

def load_yaml(yamlfile):
    f = open(yamlfile, 'r')
    data = yaml.load(f)
    f.close()
    return data['books']

def load_csv(csvfile):
    f = open(csvfile, 'r')
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        data.append(row)
    f.close()
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


@click.group()
@click.pass_context
@click.option('--repository', '-R', help='Specify repository.')
@click.version_option(version=script_version, message='v%(version)s')
def cmd(ctx, repository):
    ctx.obj['repository'] = repository


@cmd.command(help='Post books to Bruschetta.')
@click.pass_context
@click.option('--csv', is_flag=True, help='Input from CSV.')
@click.argument('input')
def post(ctx, csv, input):
    if csv:
        books = load_csv(input)
    else:
        books = load_yaml(input)
    for book in books:
        print post_book(book, ctx.obj['repository'])


@cmd.command(help='Print YAML template to post.')
@click.pass_context
def template(ctx):
    print "---"
    print "- title:"
    print "  volume:"
    print "  series:"
    print "  series_volume:"
    print "  author:"
    print "  translator:"
    print "  publisher:"
    print "  category:"
    print "  format:"
    print "  isbn:"
    print "  published_on:"
    print "  original_title:"
    print "  note:"
    print "  keyword:"
    print "  disk:"
    print "  disposed:"


@cmd.command(help='Get book informations into CSV.')
@click.pass_context
@click.option('--limit', '-l', type=int, help='Limit of getting books.')
@click.option('--offset', '-o', type=int, help='Offset.')
@click.option('--all', '-a', is_flag=True, help='Dump all books.')
def csvdump(ctx, limit, offset, all):
    if all:
        books = []
        limit = 100
        offset = 0
        while True:
            bks = get_books(ctx.obj['repository'], limit, offset)
            if not bks:
                break
            books.extend(bks)
            offset += limit
    else:
        books = get_books(ctx.obj['repository'], limit, offset)
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
        'disk',
        'disposed'
    ]

    csvwriter = csv.writer(sys.stdout, lineterminator='\n')
    csvwriter.writerow(headers)
    for book in books:
        book_data = [
            book['title'].encode('utf-8'),
            book['volume'].encode('utf-8'),
            book['series'].encode('utf-8'),
            book['series_volume'].encode('utf-8'),
            book['author'].encode('utf-8'),
            book['translator'].encode('utf-8'),
            book['publisher'].encode('utf-8'),
            book['category'].encode('utf-8'),
            book['format'].encode('utf-8'),
            book['isbn'].encode('utf-8'),
            book['published_on'].encode('utf-8'),
            book['original_title'].encode('utf-8'),
            book['note'].encode('utf-8'),
            book['keyword'].encode('utf-8'),
            book['disk'].encode('utf-8'),
        ]
        if book['disposed']:
            book_data.append('1')
        else:
            book_data.append('0')
        csvwriter.writerow(book_data)


def main():
    cmd(obj={})


if __name__ == '__main__':
    main()
