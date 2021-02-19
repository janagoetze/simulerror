'''Template code for running simulations and distance calculations'''

import sys
sys.path.append('src')
from src.misc import read_config, json2tabular
from src.simulator import Simulator
from src.measures import Distance
import os


CONFIG = "config.json"  # paths to lexicon and resources
LANGUAGES = ('nor', 'swe')  # languages
PATTERNS = ('stopping', 'velar_fronting')  # error patterns
METRICS = ('wcm', 'pcc', 'pwp', 'ipc')  # distance metrics
CORPORA = {  # corpus files to include for each language
    'nor': [
        "path_to_norwegian_frequency_list_1",
        "path_to_norwegian_frequency_list_2"
        ]
    }
# Below, specify path to OUTDIR where results are written for each pattern


def main():
    # Config file containing paths to the previously prepared transcription
    # lists and other resources needed to do the calculations
    # stays the same for all experiments
    config = read_config(CONFIG)

    # Every language accesses its own resources and corpora
    for language in LANGUAGES:
        lexicon = config['resources']['lexicon'][language]
        closed_class_words = config['resources']['closed_class_words'][language]

        OUTDIR = 'path_for_output'
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)
        phone_frequency_file = os.path.join(OUTDIR, 'phon.freq')

        corpora = CORPORA[language]

        print('\nRUNNING SIMULATIONS FOR {}\n'.format(language.upper()))
        simulator = Simulator(language, lexicon, corpora)
        simulator.token_to_phonfreq_unigram(phone_frequency_file)

        for error_pattern in PATTERNS:
            # For every pattern: simulate, then get distance measures
            print('\nRUNNING PATTERN {}'.format(error_pattern.upper()))
            outfile = os.path.join(OUTDIR, '{}.csv'.format(error_pattern))
            simulator.simulate(error_pattern)
            simulator.to_csv(outfile)

            distance = Distance(
                os.path.join(OUTDIR, '{}.csv'.format(error_pattern)),
                phone_frequency_file,
                language,
                closed_class_words
                )
            for metric in METRICS:
                print('{}:'.format(metric.upper()))
                print(json2tabular(distance.measure(metric)))
            distance.to_csv(
                os.path.join(OUTDIR, 'result_{}.csv'.format(error_pattern))
                )


if __name__ == '__main__':
    main()
