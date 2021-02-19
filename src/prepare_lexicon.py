'''commandline script to extend a lexicon with a list of transcribed words

Choosing the language will read the base lexicon from config.json. This lexicon
is taken as basis, existing entries will not be over-written. The base lexicon
can be in either the original format or in .json format.

The resulting lexicon is saved as json and can be used for simulating error
patterns on a corpus.
'''
import click
import logging
from misc import read_config
from lexicon import Lexicon
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
    '-l', '--language', type=click.Choice(
        ['eng', 'swe', 'nor'],
        case_sensitive=False
    ),
    required=True
)
@click.option('-t', '--transcriptions', type=click.Path(exists=True), multiple=True)
@click.option('-o', '--outfile', type=click.Path(), required=True, help='File to write the lexicon to (*.json)')
@click.option('--config', 'config_file', type=click.Path(), default='config.json', help='Configuration file to read from (*.json)')
def main(language, transcriptions, outfile, config_file):
    config = read_config(config_file)

    lexicon_file = config['resources']['lexicon'][language]

    lex = Lexicon(language, lexicon_file)
    for transcribed_entries in transcriptions:
        lex.extend_lexicon(transcribed_entries)

    lex.save_to_json_file(outfile, overwrite=True)
    click.echo('Lexicon written to {}. Update config.json accordingly before running simulations.'.format(outfile))


if __name__ == '__main__':
    main()
