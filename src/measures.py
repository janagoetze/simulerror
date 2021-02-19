#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from collections import namedtuple
from ast import literal_eval
import pandas as pd
import numpy as np
import csv
from phonemes import EnglishPhonemes, NorwegianPhonemes, SwedishPhonemes
from misc import read_closed_class_words
import logging

'''Calculate distance measures on the simulations'''

SimulatedPronunciation = namedtuple(
    'SimulatedPronunciation',
    [
        'token',  # index
        'frequency',  # frequency
        'original',  # transcription
        'num_C_original',
        'simulation',  # named simulation, e.g. stopping
        'num_C_changed',  # changed_consonants_stopping
        'unchanged'
    ]
)


class Distance:
    _implemented_metrics = ('ipc', 'pcc', 'pwp', 'wcm')

    def __init__(self, csvfile, phonfreq, language, closed_class_words_file=None):
        self.simulation = self._from_csv(csvfile)
        self.__pattern = os.path.basename(csvfile)
        self.phonfreq = self._csv_to_dict(phonfreq)
        self.phonemes = self._language_phonemes(language)()

        self._closed_class_words = read_closed_class_words(closed_class_words_file)

        self._add_measure_columns()

    def _add_measure_columns(self):
        for metric in self._implemented_metrics:
            self.simulation[metric] = np.nan

    def _language_phonemes(self, language):
        phoneme_mapping = {
            'nor': NorwegianPhonemes,
            'swe': SwedishPhonemes,
            'eng': EnglishPhonemes
        }
        return phoneme_mapping[language]

    def _from_csv(self, csvfile):
        def convert(item):
            if not item:
                return []
            try:
                return literal_eval(item)
            except SyntaxError:
                return []

        return pd.read_csv(csvfile,
                           quoting=csv.QUOTE_MINIMAL,
                           converters={
                                'changes': convert,
                                'original': convert,
                                'simulation': convert,
                                'transcription': convert
                           },
                           dtype={
                                'token': str,
                                'frequency': np.float64,
                                'generated': object,
                                'changed_consonants': np.int64,
                                'num_C_original': np.float64,
                                'unchanged': bool
                           }
                           )

    def _csv_to_dict(self, infile):
        d = dict()
        with open(infile, 'r', newline='') as csvfile:
            data_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL)
            for row in data_reader:
                d[row[0]] = (int(row[1]), float(row[2]))
        return d

    def to_csv(self, outfile):
        '''distance measures to table format (csv)'''

        self.simulation.to_csv(
            outfile,
            columns=[
                'token',
                'frequency',
                'transcription',
                'original',
                'generated',
                'changed_consonants',
                'num_C_original',
                'simulation',
                'unchanged',
                'ipc',
                'pcc',
                'pwp',
                'wcm'
            ],
            index=True
        )

    @staticmethod
    def stats(column):
        return {
            'N': column.size,
            'mean': column.mean(),
            'stdev': column.std(),
            'quantiles': [column.quantile(0.25),
                          column.quantile(0.5),
                          column.quantile(0.75)
                          ]
            }

    def measure(self, metric):
        '''calculate the metric and gather the stats for tokens and types

        :param metric: string, one of 'ipc', 'pcc', 'pwp', 'wcm'
        :returns: dict, the number of entries on which the calculation was done,
                  the mean, stdev and quantiles of the metric. Calculates stats
                  on types and tokens
        '''
        if metric not in self._implemented_metrics:
            raise NotImplementedError

        # calculate the metric in the corresponding column
        getattr(self, metric)()

        def multiply(item, factor):
            if np.isnan(factor):
                return []
            if np.isnan(item):
                return [np.nan]
            return [item for i in range(int(factor))]

        token_metric = pd.Series(np.array(list(map(
            multiply,
            self.simulation[metric],
            self.simulation['frequency']
        )), dtype=object))
        token_metric = token_metric.explode().dropna()

        type_stats = self.stats(self.simulation[metric])
        token_stats = self.stats(token_metric)

        return {
            '{}_on_types'.format(metric): type_stats,
            '{}_on_tokens'.format(metric): token_stats
        }

    def ipc(self):
        '''Index of Phonetic Complexity'''

        self.simulation['ipc'] = np.array(list(map(
            self._calculate_ipc,
            self.simulation['token'],
            self.simulation['simulation'],
            self.simulation['original']
        )), dtype=object)

    def _calculate_ipc(self, token, transcription, original):
        '''Calculate Index of Phonetic Complexity score based on
        - number of dorsal consonants
        - number of fricative, affricate, or liquid consonants
        - number of rhotic vowels
        - whether the transcription ends with a consonant
        - number of syllables
        - single-consonant variegation
        - number of consonant clusters
        - number of heterorganic clusters

        :param token: the token string
        :param transcription: the transcription after applied error pattern
        :param original: the transcription before applied error pattern
        :returns: int, the score
        '''
        if token in self._closed_class_words:
            return np.nan

        acc_points = []

        acc_points.append(
            self.number_of_dorsal_consonants(transcription)
            - self.number_of_dorsal_consonants(original)
        )

        acc_points.append(
            self.number_of_fricative_affricate_liquid_consonants(transcription)
            - self.number_of_fricative_affricate_liquid_consonants(original)
        )

        acc_points.append(
            self.number_of_rhotic_vowels(transcription)
            - self.number_of_rhotic_vowels(original)
        )

        if (
          self.ends_with_consonant(transcription)
          and not self.ends_with_consonant(original)
          ):
            diff = 1
        elif (
          self.ends_with_consonant(original)
          and not self.ends_with_consonant(transcription)
          ):
            diff = -1
        else:
            diff = 0
        acc_points.append(diff)

        if (
          self.number_of_syllables(transcription) > 2
          and not self.number_of_syllables(original) > 2):
            diff = 1
        elif (
          self.number_of_syllables(original) > 2
          and not self.number_of_syllables(transcription) > 2):
            diff = -1
        else:
            diff = 0
        acc_points.append(diff)

        acc_points.append(
            self.S_C_variegation(transcription)
            - self.S_C_variegation(original)
        )

        acc_points.append(
            self.number_of_consonant_clusters(transcription, 'ipc')
            - self.number_of_consonant_clusters(original, 'ipc')
        )

        acc_points.append(
            self.number_of_heterorg_clusters(transcription)
            - self.number_of_heterorg_clusters(original)
        )

        logging.debug('IPC,"{}","{}","{}","{}",{}'.format(self.__pattern,
                                                          token,
                                                          original,
                                                          transcription,
                                                          ','.join(map(lambda x: str(x), acc_points))))
        return sum(acc_points)

    def pcc(self):
        '''Percent Consonants Correct
        Calculates the ratio b/w unchanged consonants and all consonants
        '''
        self.simulation['pcc'] = np.array(list(map(
            self._calculate_pcc,
            self.simulation['num_C_original'],
            self.simulation['changed_consonants']
        )), dtype=object)

    def _calculate_pcc(self, number_of_consonants, number_of_changes):
        if number_of_consonants == 0:
            return 1
        elif np.isnan(number_of_consonants):
            return np.nan
        else:
            number_of_unchanged = number_of_consonants - number_of_changes
            return number_of_unchanged / number_of_consonants

    def pwp(self):
        '''Proportion of Whole-Word Proximity
        pmlu_observed / pmlu_target (Phonological Mean Length of Utterance)
        '''

        self.simulation['pwp'] = np.array(list(map(
            self._calculate_pwp,
            self.simulation['simulation'],
            self.simulation['original'],
            self.simulation['num_C_original'],
            self.simulation['changed_consonants']
        )), dtype=object)

    def _calculate_pwp(self,
                       transcription,
                       original,
                       number_of_consonants,
                       number_of_changed_consonants
                       ):
        # pmlu: Phonological Mean Length of Utterance
        pmlu_original = (self.number_of_segments(original)
                         + number_of_consonants
                         )
        pmlu_transcription = (self.number_of_segments(transcription)
                              + number_of_consonants
                              - number_of_changed_consonants
                              )

        if pmlu_original > 0:
            pwp = pmlu_transcription / pmlu_original
        else:
            pwp = 0

        return pwp

    def wcm(self):
        '''Word Complexity Measure WCM
        '''
        self.simulation['wcm'] = np.array(list(map(
            self._calculate_wcm,
            self.simulation['simulation'],
            self.simulation['original']
        )), dtype=object)

    def _calculate_wcm(self, transcription, original):
        '''Calculate Word Complexity score based on
        - number of syllables
        - stress on initial syllable
        - whether the pronunciation ends in a consonant
        - number of consonant clusters
        - number of velar consonants
        - number of liquids and rhotics
        - number of fricatives and affricates
        - number of voiced fricatives
        - number of long front rounded vowels

        :param transcription: the transcription after applied error pattern
        :param original: the transcription before applied error pattern
        :returns: int, the score
        '''
        acc_points = []

        syll_original = self.number_of_syllables(original)
        syll_transcription = self.number_of_syllables(transcription)
        if syll_transcription > 2 and not syll_original > 2:
            diff = 1
        elif syll_original > 2 and not syll_transcription > 2:
            diff = -1
        else:
            diff = 0
        acc_points.append(diff)

        non_initial_stress_transcr = self.stress_on_non_initial_syllable(transcription)
        non_initial_stress_orig = self.stress_on_non_initial_syllable(original)
        diff = 0
        if non_initial_stress_transcr and not non_initial_stress_orig:
            diff = 1
        elif non_initial_stress_orig and not non_initial_stress_transcr:
            diff = -1
        acc_points.append(diff)

        final_consonant_transcription = self.ends_with_consonant(transcription)
        final_consonant_original = self.ends_with_consonant(original)
        diff = 0
        if final_consonant_transcription and not final_consonant_original:
            diff = 1
        elif final_consonant_original and not final_consonant_transcription:
            diff = -1
        acc_points.append(diff)

        acc_points.append(
            self.number_of_consonant_clusters(transcription, 'wcm')
            - self.number_of_consonant_clusters(original, 'wcm')
            )

        acc_points.append(
            self.number_of_velar_consonants(transcription)
            - self.number_of_velar_consonants(original)
            )

        acc_points.append(
            self.number_of_liquid_or_rhotic_consonants(transcription)
            - self.number_of_liquid_or_rhotic_consonants(original)
            )

        acc_points.append(
            self.number_of_fricative_or_affricate_consonants(transcription)
            - self.number_of_fricative_or_affricate_consonants(original)
        )

        acc_points.append(
            self.number_of_voiced_fricatives(transcription)
            - self.number_of_voiced_fricatives(original)
            )

        acc_points.append(
            self.number_of_long_front_rounded_vowels(transcription)
            - self.number_of_long_front_rounded_vowels(original)
        )

        return sum(acc_points)

    def number_of_segments(self, pronunciation):
        '''count number of consonants and vowels (remove all stress)
        :param pronunciation: list, transcription
        :returns: int, length of remaining transcription
        '''
        pronunciation = self._remove_stress_word(pronunciation)
        pronunciation = self._remove_syllable_boundary(pronunciation)
        return len(pronunciation)

    def number_of_dorsal_consonants(self, transcription):
        # check in the corresponding IPC Feature list
        return sum(
            [int(self.phonemes.dorsal_consonant(p)) for p in transcription]
        )

    def number_of_fricative_affricate_liquid_consonants(self, transcription):
        return sum(
            [int(self.phonemes.fricative_affricate_liquid_consonant(p)) for p in transcription]
        )

    def number_of_rhotic_vowels(self, transcription):
        # ENG only: check if vowel followed by /r/
        return self.phonemes.rhotic_vowels(
            transcription,
            self._vowel_positions(transcription)
        )

    def number_of_velar_consonants(self, transcription):
        return sum([int(self.phonemes.velar_consonant(p)) for p in transcription])

    def number_of_liquid_or_rhotic_consonants(self, transcription):
        return sum([int(self.phonemes.liquid_or_rhotic_consonant(p)) for p in transcription])

    def number_of_fricative_or_affricate_consonants(self, transcription):
        return sum([int(self.phonemes.fricative_or_affricate_consonant(p)) for p in transcription])

    def number_of_voiced_fricatives(self, transcription):
        return sum([int(self.phonemes.voiced_fricative(p)) for p in transcription])

    def number_of_long_front_rounded_vowels(self, transcription):
        return sum([int(self.phonemes.long_front_rounded_vowel(p)) for p in transcription])

    def stress_on_non_initial_syllable(self, transcription):
        # "A:$b@lt
        # ""9*Y$%gru0$p@r
        # grA$"fi:
        return "\"" not in transcription

    def S_C_variegation(self, phonetic_transcription):
        # single consonant variegation

        def get_cons(pron, vows):
            sing_cons = []
            # word-initial SC?
            if len(vows) > 0 and vows[0] == 1:
                sing_cons.append(pron[0])
            # word-internal SC?
            for i in range(len(vows)-1):
                if vows[i+1] - vows[i] == 2:
                    sing_cons.append(pron[vows[i]+1])
                elif vows[i+1] - vows[i] > 2:
                    sing_cons.append("CLUSTER")
            # word-final SC?
            if len(vows) > 0 and (len(pron) - 1) - vows[-1] == 1:
                sing_cons.append(pron[-1])

            return sing_cons

        pron = self._remove_stress_word(phonetic_transcription)
        pron = self._remove_syllable_boundary(pron)
        vows = self._vowel_positions(pron)
        sing_cons = get_cons(pron, vows)
        score = self.phonemes.score_variegation(sing_cons)
        return score

    def number_of_heterorg_clusters(self, phonetic_transcription):
        pron = self._remove_stress_word(phonetic_transcription)
        pron = self._remove_syllable_boundary(pron)
        vowels = self._vowel_positions(pron)

        clusters = []
        # word-initial
        if len(vowels) > 0 and vowels[0] > 1:
            clusters.append(pron[:vowels[0]])
        # word-internal
        for i in range(len(vowels)-1):
            if vowels[i+1] - vowels[i] > 2:
                clusters.append(pron[vowels[i]+1:vowels[i+1]])
        # word-final
        if len(vowels) > 0 and len(pron)-1 - vowels[-1] > 1:
            clusters.append(pron[vowels[-1]+1:len(pron)])
        return self.phonemes.number_of_heterorg_clusters(clusters)

    def _remove_stress_word(self, phonetic_transcription):
        return [p for p in phonetic_transcription if p not in ("\"\"", "\"", "%", chr(164))]

    def _remove_syllable_boundary(self, pron):
        return [p for p in pron if p not in ("$", "_")]

    def _vowel_positions(self, pron):
        # return the positions in the list that are vowels
        vowels = []
        for i in range(len(pron)):
            """ all transcriptions are now in X-sampa
            if pron[i][-1] in ["0", "1", "2"]:
                p = pron[i][:-1]
            """
            if (
              pron[i] in self.phonemes.vowels['phoneme'].tolist()
              or pron[i] in self.phonemes.diphthongs['phoneme'].tolist()
              ):
                vowels.append(i)
        return vowels

    def _syllable_positions(self, pron):
        '''
        :param pron: list of phonemes
        :returns: list, the positions in the list that are syllable boundaries
        '''
        markers = []
        for i in range(len(pron)):
            if pron[i] == "$":
                markers.append(i)
        return markers

    def ends_with_consonant(self, phonetic_transcription):
        if not phonetic_transcription:
            return False
        else:
            return phonetic_transcription[-1] in self.phonemes.consonants

    def number_of_syllables(self, phonetic_transcription):
        # count syllable delimiters
        return phonetic_transcription.count('$') + 1

    def number_of_consonant_clusters(self, phonetic_transcription, metric):
        # WCM counts clusters only within syllables
        # IPC counts clusters over syllable boundaries

        # check at which positions the vowels are
        c = 0
        pron = self._remove_stress_word(phonetic_transcription)

        if metric == "ipc":
            pron = self._remove_syllable_boundary(pron)
        vowels = self._vowel_positions(pron)

        if metric == "wcm":
            # count syllable marker with the vowels
            vowels.extend(self._syllable_positions(pron))

        vowels.sort()
        # word-initial
        if len(vowels) > 0 and vowels[0] > 1:
            c += 1

        # word-internal
        for i in range(len(vowels)-1):
            if vowels[i+1] - vowels[i] > 2:
                # don't count norwegian /nn=/ as a cluster!
                if not (pron[i-3] == "n" and pron[i-2] == "n="):
                    c += 1

        # word-final
        if len(vowels) > 0 and (len(pron)-1 - vowels[-1]) > 1:
            # don't count norwegian /nn=/ as a cluster!
            if not (pron[-2] == "n" and pron[-1] == "n="):
                c += 1

        return c
