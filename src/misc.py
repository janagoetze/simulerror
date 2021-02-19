import json
import click
from tabulate import tabulate


def read_config(config):
    try:
        with open(config) as json_data_file:
            conf = json.load(json_data_file)
    except FileNotFoundError:
        click.echo('Config file does not exit: {}'.format(config))
        exit(1)
    else:
        return conf


def read_closed_class_words(filename):
    closed_class_words = []
    if not filename:
        return closed_class_words
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n")
            closed_class_words.append(line)
    return closed_class_words


def json2tabular(json_data):
    header = ['N', 'mean', 'stdev', 'quantiles']
    table = []
    for item in json_data:
        row = []
        row.append(item)
        row.extend([json_data[item][head] for head in header])
        table.append(row)
    return tabulate(table, headers=header)
