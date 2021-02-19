import os
import click
import logging
from measures import Distance
from misc import read_config, json2tabular
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s',
                    filename='simulate.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)


@click.command()
@click.option('-f', '--format', type=click.Choice(['json', 'table']), default='json')
@click.option(
    '-d', '--distance_metric',
    type=click.Choice(
        ['ipc', 'pcc', 'pwp', 'wcm'],
        case_sensitive=False
    ),
    multiple=True,
    required=True)
@click.option(
    '-l', '--language', type=click.Choice(
        ['eng', 'swe', 'nor'],
        case_sensitive=False
    ),
    required=True)
@click.option('-i', '--error-corpus', 'indir', type=click.Path(exists=True), required=True)
@click.option('-o', '--outdir', type=click.Path(), required=True, help='csv file to write simulation to')
@click.option('--config', 'config_file', type=click.Path(), default='config.json', help='Configuration file to read from (*.json)')
def main(indir, language, distance_metric, outdir, config_file, format):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    config = read_config(config_file)
    closed_class_words = config['resources']['closed_class_words'][language]

    PHONE_FREQ = os.path.join(os.path.dirname(indir), 'phon.freq')

    distance = Distance(indir, PHONE_FREQ, language, closed_class_words)
    for metric in distance_metric:
        result = distance.measure(metric)
        if format == 'json':
            click.echo('{}: {}'.format(metric.upper(), result))
        elif format == 'table':
            click.echo('{}:'.format(metric.upper()))
            click.echo(json2tabular(result))
    distance.to_csv(os.path.join(outdir, 'result.csv'))


if __name__ == '__main__':
    main()
