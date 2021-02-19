from simulator import Simulator
import os
import click
import logging
from misc import read_config
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s',
                    filename='simulate.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)


@click.command()
@click.option(
    '-e', '--error_pattern',
    type=click.Choice(
        [
            'cluster_reduction',
            'coronal_backing',
            'pretonic_syllable_deletion',
            'r_weakening',
            'stopping',
            'velar_fronting'
        ],
        case_sensitive=False
    ),
    required=True
)
@click.option(
    '-l', '--language', type=click.Choice(
        ['eng', 'swe', 'nor'],
        case_sensitive=False
    ),
    required=True
)
@click.option('-c', '--corpus', 'corpora', type=click.Path(exists=True), multiple=True, required=True)
@click.option('-o', '--outdir', type=click.Path(), required=True, help='File to write simulation to (*.csv)')
@click.option('--config', 'config_file', type=click.Path(), default='config.json', help='Configuration file to read from (*.json)')
def main(corpora, language, error_pattern, outdir, config_file):
    config = read_config(config_file)

    lexicon = config['resources']['lexicon'][language]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    simulator = Simulator(language, lexicon, corpora)

    simulator.token_to_phonfreq_unigram(os.path.join(outdir, 'phon.freq'))

    outfile = os.path.join(outdir, '{}.csv'.format(error_pattern))
    simulator.simulate(error_pattern)
    simulator.to_csv(outfile)


if __name__ == '__main__':
    main()
