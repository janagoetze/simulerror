#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from patterns import CORONAL_BACKING, R_WEAKENING, STOPPING, VELAR_FRONTING
from lexicon import Lexicon
from corpus import Corpus
from progress.bar import Bar
from collections import Counter
from itertools import repeat
import logging
import csv

'''Simulator class that applies error patterns'''


class Simulator:
    def __init__(self, language, lexicon, corpora, n=0):
        self.lexicon = Lexicon(language, lexicon)
        self.corpus = Corpus(corpora)

        self.simulation = self._pool_corpus_and_lexicon()

        self.N = n
        self._num_consonants_changed = 0

        self.phonfreq = self.token_to_phonfreq_unigram()
        self.total_phonfreq = 0  # updated with phonfreq

    def _pool_corpus_and_lexicon(self):
        '''join the corpus and lexicon DataFrames'''
        df = pd.concat([self.corpus.data, self.lexicon.data], axis=1, sort=False)
        df.index.name = 'token'
        return df[df['frequency'] > 0]

    def to_csv(self, outfile):
        '''simulation to table format (csv)'''
        self.simulation['unchanged'] = self.simulation['original'] == self.simulation['transcription']
        self.simulation['print'] = self.simulation['original'].notna()
        self.simulation[self.simulation['print']].to_csv(
            outfile,
            columns=[
                'frequency',
                'transcription',
                'original',
                'generated',
                'changed_consonants',
                'changes',
                'num_C_original',
                'simulation',
                'unchanged'
            ],
            index=True
        )

    def simulate(self, pattern):
        patterns = {
            'coronal_backing': CORONAL_BACKING,
            'r_weakening': R_WEAKENING,
            'stopping': STOPPING,
            'velar_fronting': VELAR_FRONTING
        }
        replace = patterns.get(pattern, None)
        if not replace and pattern not in ('cluster_reduction', 'pretonic_syllable_deletion'):
            raise NotImplementedError
        else:
            # create or reset column, do the transformation
            # NB: this assumes that results are written to file in between
            # FIXME: name column after the type of simulation which means the
            # column name will need to be specified for the Distance class
            self.simulation['simulation'] = self.simulation['transcription']

            if replace:
                self._replace_sounds(replace)
            elif pattern == 'pretonic_syllable_deletion':
                self._pretonic_syllable_deletion()
            elif pattern == 'cluster_reduction':
                self._cluster_reduction()

    def _cluster_reduction(self):
        """ replaces sequence of sounds with one of them
        """
        column = 'simulation'
        change_count_column = 'changed_consonants'
        self.simulation[change_count_column] = 0

        count_affected_words = 0
        count_words = 0

        self.simulation[[column, change_count_column]] = np.array(list(map(
            self._reduce_cluster,
            self.simulation[column]
        )), dtype=object)

        # update counts
        change_count = self.simulation[change_count_column]
        entry_count = change_count.where(change_count > 0)
        affected = len(entry_count.dropna())
        count_words += affected

        # multiply word frequency with number of changed consonants in word
        change_count = self.simulation[change_count_column] * self.simulation['frequency']
        self._num_consonants_changed += int(change_count.sum())

        word_count = self.simulation[change_count_column].where(self.simulation[change_count_column] > 0)
        count_affected_words += len(word_count.dropna())

        return {
            'count_affected_words': count_affected_words,  # how many entries were affected
            'count_words': count_words,  # how many entries were affected
            'changed_consonants': int(self.simulation[change_count_column].sum()),
            'num_consonants_changed': self._num_consonants_changed
        }

    def _reduce_cluster(self, pron):
        last_match = False
        trigram_cluster = 0
        applied_n = 0
        new_trans = []
        if isinstance(pron, float) and np.isnan(pron):
            return pron, applied_n

        for i, p in enumerate(pron):
            if i < len(pron) - 1:
                # Pattern 0: /s/ + Plosive + Approx => Plosive
                if (
                  p == "s"
                  and i < len(pron) - 2
                  and pron[i+1] in self.lexicon.phonemes.plosives
                  and pron[i+2] in self.lexicon.phonemes.approximants
                  ):
                    applied_n += 2
                    trigram_cluster = 2

                # Pattern 1: Obstruent + Approximant => Obstruent
                elif (
                  trigram_cluster == 0
                  and p in self.lexicon.phonemes.obstruents
                  and pron[i+1] in self.lexicon.phonemes.approximants
                  ):
                    last_match = True
                    applied_n += 1
                    new_trans.append(p)

                # Pattern 2: /s/ + Plosive => Plosive
                elif p in ("s", "s`") and pron[i+1] in self.lexicon.phonemes.plosives:
                    applied_n += 1

                # Pattern 3: /s/ + Nasal => Nasal
                elif p in ("s", "s`") and pron[i+1] in self.lexicon.phonemes.nasals:
                    applied_n += 1

                # Pattern 4: /s/ + Approx => /s/
                elif p in ("s", "s`", "S") and pron[i+1] in self.lexicon.phonemes.approximants:
                    last_match = True
                    applied_n += 1
                    new_trans.append(p)

                # Pattern 5: Fric + Liq/Glide => Fric
                elif p in self.lexicon.phonemes.fricatives and pron[i+1] in self.lexicon.phonemes.liquidGlides:
                    last_match = True
                    applied_n += 1
                    new_trans.append(p)

                # Pattern 6: Plosive + (/v/|nasal) => Plosive
                elif (
                  trigram_cluster == 0
                  and p in self.lexicon.phonemes.plosives
                  and (pron[i+1] == "v" or pron[i+1] in self.lexicon.phonemes.nasals)
                  and not pron[i+1] in self.lexicon.phonemes.syllabic
                  ):
                    last_match = True
                    applied_n += 1
                    new_trans.append(p)

                # Pattern 7: /s/ + /v/ => /v/
                elif p in ("s", "s`") and pron[i+1] == "v":
                    applied_n += 1

                else:
                    if trigram_cluster == 1:
                        trigram_cluster = 0
                    elif not last_match:
                        new_trans.append(p)
                        if trigram_cluster == 2:
                            trigram_cluster = 1
                    last_match = False
            else:
                if not last_match:
                    new_trans.append(p)

        return new_trans, applied_n

    def _pretonic_syllable_deletion(self):
        '''delete syllables before the main stress "
        '''

        column = 'simulation'
        change_count_column = 'changed_consonants'
        self.simulation[change_count_column] = 0

        count_affected_words = 0
        count_words = 0

        self.simulation[[column, change_count_column]] = np.array(list(map(
            self._delete_unstressed_syllables,
            self.simulation[column]
        )), dtype=object)

        # update counts
        change_count = self.simulation[change_count_column]
        entry_count = change_count.where(change_count > 0)
        affected = len(entry_count.dropna())
        count_words += affected

        # multiply word frequency with number of changed consonants in word
        change_count = self.simulation[change_count_column] * self.simulation['frequency']
        self._num_consonants_changed += int(change_count.sum())

        word_count = self.simulation[change_count_column].where(self.simulation[change_count_column] > 0)
        count_affected_words += len(word_count.dropna())

        return {
            'count_affected_words': count_affected_words,  # how many entries were affected
            'count_words': count_words,  # how many entries were affected
            'changed_consonants': int(self.simulation[change_count_column].sum()),
            'num_consonants_changed': self._num_consonants_changed
        }

    def _delete_unstressed_syllables(self, pron):
        pron, changed_consonants_1 = self._delete_pretonic_syllable(pron)
        pron, changed_consonants_2 = self._delete_unstressed_inbetween(pron)
        return pron, changed_consonants_1 + changed_consonants_2

    def _delete_pretonic_syllable(self, pron):
        '''delete everything before the main stress "
        '''

        changed_consonants = 0
        if isinstance(pron, float) and np.isnan(pron):
            return pron, changed_consonants
        elif "\"" not in pron:
            return pron, changed_consonants
        else:
            phone = 0
            removed_sounds = []
            while pron[phone] != "\"":
                removed_sounds.append(pron[phone])
                phone += 1

            pron = pron[phone:]
            changed_consonants = sum(
              [
                True for p in removed_sounds
                if p in self.lexicon.phonemes.consonants
              ]
            )
            return pron, changed_consonants

    def _delete_unstressed_inbetween(self, pron):
        ''' delete syllables between main stressed and secondary stressed
        syllables
        ""S$S$S...$%S => ""S$S$%S
        /""le:$ve$pa$%stej/ => /""le:$ve$%stEj/
        /""vaks$ka$bI$%net/ => /""vaks$ka$%net/
        '''

        changed_consonants = 0
        if isinstance(pron, float) and np.isnan(pron):
            return pron, changed_consonants
        elif "%" not in pron:
            return pron, changed_consonants
        else:
            if "%" in pron:
                i = 0
                removed_sounds = []
                new_trans = []
                start_removing = False
                stop_removing = False
                sylls_after_main_stress = 0
                seen_main_stress = False

                for sound in pron:
                    remove = False
                    if sound == "%":
                        start_removing = False
                        stop_removing = True
                    elif start_removing and not stop_removing:
                        removed_sounds.append(sound)
                        remove = True
                        i += 1
                    elif sylls_after_main_stress < 2 and not start_removing:
                        if sound == "\"":
                            seen_main_stress = True
                        elif sound == "$" and seen_main_stress:
                            sylls_after_main_stress += 1

                    if sylls_after_main_stress > 1 and not stop_removing:
                        start_removing = True

                    if not remove:
                        new_trans.append(sound)

                pron = new_trans
                changed_consonants = sum(
                  [
                    True for p in removed_sounds
                    if p in self.lexicon.phonemes.consonants
                  ]
                )

            return pron, changed_consonants

    def _replace_sounds(self, patterns):
        '''replace all patterns in an entry

        - add rows to the table to count which substitution was applied how many times

        - patterns are substitutions
        - column is the error pattern that consists of at least one
          substitution (old, new)

        - substitution_count_column counts the number of changes for the
          single pair
        - change_count_column counts the number of changes for the whole error
          pattern (sum of all substitutions)

        '''
        column = 'simulation'
        change_count_column = 'changed_consonants'
        self.simulation[change_count_column] = 0

        logging.info('Running simulation with {} substitutions:'.format(len(patterns)))
        counter = 0
        count_affected_words = 0
        count_words = 0
        for (old, new) in patterns.items():
            substitution_count_column = 'changed_consonants_{}_{}'.format(old, new)
            self.simulation[substitution_count_column] = 0

            counter += 1
            is_consonant = old in self.lexicon.phonemes.consonants

            self.simulation[[column, substitution_count_column]] = np.array(list(map(
                self._replace_sound_by_row,
                self.simulation[column],
                repeat(old),
                repeat(new),
                repeat(is_consonant)
            )), dtype=object)

            # update counts
            substitution_count = self.simulation[substitution_count_column]

            self.simulation[change_count_column] = \
                self.simulation[change_count_column] + substitution_count
            logging.info('\t{}. Replaced {} with {} {} times'.format(counter, old, new, int(substitution_count.sum())))

            entry_count = substitution_count.where(substitution_count > 0)
            affected = len(entry_count.dropna())
            count_words += affected
            logging.info('Replaced {} in {} words (types)'.format(old, affected))

        # multiply word frequency with number of changed consonants in word
        change_count = self.simulation[change_count_column] * self.simulation['frequency']
        self._num_consonants_changed += int(change_count.sum())

        word_count = self.simulation[change_count_column].where(self.simulation[change_count_column] > 0)
        count_affected_words += len(word_count.dropna())

        # FIXME: is this necessary?
        # recompute the inverted lexicon
#        self.lexicon.inverted = self.lexicon.invert_lexicon()

        return {
            'count_affected_words': count_affected_words,  # how many entries were affected
            'count_words': count_words,  # how many entries were affected
            'changed_consonants': int(self.simulation[change_count_column].sum()),
            'num_consonants_changed': self._num_consonants_changed
        }

    def _replace_sound_by_row(self, pron, old, new, is_consonant):
        changed_consonants = 0
        if isinstance(pron, float) and np.isnan(pron):
            return pron, changed_consonants
        elif old not in pron:
            return pron, changed_consonants
        else:
            return self._replace_sound(pron, old, new, is_consonant)

    def _replace_sound(self, pron, old, new, is_consonant):
        new_trans = []
        changed = 0
        for i, sound in enumerate(pron):
            if sound != old:
                new_trans.append(sound)
            else:
                # check for context
                if Simulator._replace_in_context(pron, i, old, new):
                    new_trans.append(new)
                else:
                    logging.debug('DROPPED SOUND {}'.format(old))
                # individual change count
                if is_consonant:
                    changed += 1

        logging.debug('NEW transcription: {}-->{}'.format(pron, new_trans))
        return new_trans, changed

    @staticmethod
    def _replace_in_context(pron, index, old, new):
        # velar_fronting: /jakt/ -> /jat/ (not /jatt/)
        # velar_fronting: /vaNn/ -> /van/ (not /vann/), signal -> /sI$"nA:l/
        # coronal_backing: /li:kt/ -> /li:kt/ (not /li:kk/)
        # coronal_backing: "adventures": /{g$"vEN$tS3:z/ -> /{g$"vEN$kS3:z/
        # stopping: /stranden/ -> /tranden/ (not /ttranden/)
        # stopping: /skull/ -> /ku0l/ (not /tku0l/)
        # stopping: k�kssk�p -> /""t9t$%ko:p/
        # stopping: k�nts -> /"tent/ (not /"tentt/)
        j = index
        if index != len(pron) - 1:
            while j < len(pron) - 1 and pron[j+1] in ['"', '""', '%', '$', chr(164)]:
                j += 1
        k = index
        if index != 0:
            while pron[k-1] in ['"', '""', '%', '$', chr(164)]:
                k -= 1

        if old == "k" and new == "t" and index != len(pron) - 1:
            if pron[j+1] != "t":
                return True
        elif old in ["t", "t`"] and new == "k" and k > 0:
            if pron[k-1] != "k":
                return True
        elif old in ["d", "d`"] and new == "g" and k > 0:
            if pron[k-1] != "g":
                return True
        elif old == "N" and new == "n" and index != len(pron) - 1:
            if pron[j+1] != "n":
                return True
        elif old == "s" and new == "t" and index != len(pron) - 1:
            if (pron[k-1] != "t"
                    and pron[index+1] not in ['t', 'k', 'p', 'b', 's', 'v', 'n', 'l']
                    and pron[j+1] != "t"):
                return True
        elif old == "s`" and new == "t`" and index != len(pron) - 1:
            if (pron[k-1] != "t`"
                    and pron[index+1] not in ['t`', 's`']
                    and pron[j+1] != "t`"):
                return True
        elif old == "s" and new == "t" and k > 0:
            if pron[k-1] not in ["t", "t`"]:
                return True
        elif old == "s`" and new == "t`" and k > 0:
            if pron[k-1] not in ["t", "t`"]:
                return True
        else:
            return True

    def token_to_phonfreq_unigram(self, outfile=None, mode='original'):
        '''convert the token frequency list to a phone frequency list
        returns a dictionary
        mode==original : count from the original transcriptions
        mode==transcription : count the current transcriptions (e.g. after applying an error pattern)
        '''
        d = Counter()

        selection = self.simulation.loc[lambda df: df['frequency'] >= self.N, :]
        selection = selection.dropna(subset=['transcription'])

        for index, row in selection.iterrows():
            pronunciation = row['original']
            if mode == 'transcription':
                pronunciation = row['transcription']
            for sound in pronunciation:
                # disregard non-segments (syllable boundaries, stress)
                if sound in self.lexicon.phonemes.inventory['phoneme'].to_list():
                    # to handle NST lexica where traces of E still exist...
                    if sound == 'E':
                        sound = 'e'
                    d[sound] += row['frequency']

        self.total_phonfreq = sum(d.values())

        if outfile:
            with open(outfile, 'w', newline='') as csvfile:
                progress = Bar('Writing phone frequencies ', max=len(d))
                phon_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                for phon, freq in d.items():
                    progress.next()
                    phon_writer.writerow([phon, int(freq), freq/self.total_phonfreq])
                progress.finish()
            logging.info('Written phone frequencies to {}'.format(outfile))

        return d
