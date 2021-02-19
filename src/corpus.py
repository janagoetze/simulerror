#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging
import pandas as pd
from progress.counter import Counter

'''Representation of a frequency list

pandas DataFrame table
columns: token (index), frequency
'''


class Corpus:
    def __init__(self, corpora):
        self._freq = {}  # token:frequency
        self.data = pd.DataFrame()

        self.threshold = None
        self.admissible_chars = re.compile('[a-zäöåüøéèòæœ̃þð]')  # TODO: use it

        self._corpora = corpora  # list of files that was read from

        self.del_instances = 0
        self.del_entries = 0

        self._read_corpus_files(self._corpora)

    def __getitem__(self, token):
        return self.data.at[token, 'frequency']

    def __setitem__(self, token, value):
        self.data.loc[token]['frequency'] = value

    def __len__(self):
        '''number of entries'''
        return self.data.shape[0]

    def __token_count(self):
        '''number of tokens'''
        return self.data['frequency'].sum()

    def _read_corpus_files(self, corpuslist):
        '''read corpus from frequency list
        the format must be Freq\tToken
        returns a dictionary token:freq
        '''

        logging.info('Processing {} corpus data files'.format(len(corpuslist)))

        for corpusfile in corpuslist:
            with open(corpusfile, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip('\n')
                    try:
                        item = line.split('\t')
                        self._add_entry(item[1], int(item[0]))
                    except IndexError:
                        logging.debug('Ignoring line: {} (IndexError)'.format(line))
                    except ValueError:
                        logging.debug('Ignoring line: {} (ValueError)'.format(line))
            self._normalize_tokens()

        # DataFrame's update() method overwrites values, so we'll do
        # manipulation on the dict() before creating the pandas DataFrame object
        self.data = pd.DataFrame.from_dict(self._freq, orient='index', columns=['frequency'])
        logging.info('No. corpus entries: {}'.format(len(self)))
        logging.info('No. corpus tokens: {}'.format(self.__token_count()))

    def _clean_frequency_list(self):
        '''remove any token that contains a character that is not a letter +
        remove any token with freq < threshold
        '''
        delete = []  # list of tokens to delete

        for word in self._freq:
            # FIXME: can this be elifs?
            if self._freq[word] < int(self.threshold):
                delete.append(word)
            if re.search(r"[^a-zäöåüøéèòæœ̃þð'’_\-\­+]", word):
                delete.append(word)
            # look for single symbols
            if len(word) == 1 and re.match("[^a-zäöåüøéèòæœ̃þð]", word):
                delete.append(word)

        if '' in self._freq:
            delete.append('')

        self._delete_and_log(delete)

    def _normalize_tokens(self):
        '''make sure all the lists use the same conventions e.g. ´ --> ' '''
        delete = []
        for word in self._freq:
            if re.search("[’´]", word):
                delete.append(word)
                replace = word.replace("´", "'")
                replace = word.replace("’", "'")
                self._add_entry(replace, self._freq[word])
        self._delete_and_log(delete)

    def _add_entry(self, token, freq):
        token = token.lower()
        if token:
            if token not in self._freq:
                self._freq[token] = 0
            self._freq[token] += freq

    def _delete_and_log(self, delete):
        delete = list(set(delete))
        for remove in delete:
            self.del_instances += self._freq[remove]
            self.del_entries += 1
            del self._freq[remove]

        delete.sort()
        for remove in delete:
            # TODO: self.log -> choose correct log file
            logging.info('REMOVED {}'.format(remove))
