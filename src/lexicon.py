#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Represent Lexicon

pandas DataFrame table
columns: token (index), transcription, original, generated, changed_consonants, changes
"""


import os
import json
import logging
import pandas as pd
from collections import OrderedDict
from progress.counter import Counter
from phonemes import EnglishPhonemes, NorwegianPhonemes, SwedishPhonemes


class LexiconEntry:
    def __init__(self, transcription, generated=False):
        self.transcription = transcription
        self.original = transcription
        self.generated = generated
        self.changed_consonants = 0
        self.changes = ['' for i in range(len(self.transcription))]

    def __repr__(self):
        return 'LexiconEntry(transcription={}, generated={}, original={}, changed_consonants={}, changes={})'.format(
            self.transcription,
            self.generated,
            self.original,
            self.changed_consonants,
            self.changes
        )

    def unchanged(self):
        return self.transcription == self.original


class Lexicon:
    def __init__(self, language, filename, from_original=False):
        '''filename can be a json, or original
        '''
        self._entries = {}
        self._inverted = {}
        self.language = language
        self.phonemes = self._language_phonemes(language)()
        self.sampa = False

        self._read_lexicon(filename, from_original)
        if filename.endswith('json'):
            self.sampa = True

        self.data = self._dict_to_dataframe()
        self.convert_to_sampa()

        self.save_to_json_file(filename)

    def __getitem__(self, entry):
        return self.data.loc[entry]

    def __len__(self):
        '''number of entries'''
        return self.data.shape[0]

    @property
    def _phonemes(self):
        return list(reversed(OrderedDict(sorted(list(self.phonemes.inventory.to_records(index=False)), key=lambda t: t[0]))))

    def _language_phonemes(self, language):
        phoneme_mapping = {
            'nor': NorwegianPhonemes,
            'swe': SwedishPhonemes,
            'eng': EnglishPhonemes
        }
        return phoneme_mapping[language]

    def _dict_to_dataframe(self, dict_entries=None):
        if not dict_entries:
            dict_entries = self._entries
        return pd.DataFrame(
            data=[[
                dict_entries[entry].transcription,
                dict_entries[entry].original,
                dict_entries[entry].generated,
                dict_entries[entry].changed_consonants,
                dict_entries[entry].changes,
                self.number_of_consonants(entry, original=True)
            ] for entry in dict_entries
            ],
            index=[entry for entry in dict_entries.keys()],
            columns=[
                'transcription',
                'original',
                'generated',
                'changed_consonants',
                'changes',
                'num_C_original'
            ]
        )

    def _read_lexicon(self, filename, from_original=False):
        if not filename.endswith('.json') and not from_original:
            # check whether the file has already been read
            if os.path.exists(filename.replace('.pron', '.json')):
                filename = filename.replace('.pron', '.json')
            elif os.path.exists(filename + '.json'):
                filename = filename + '.json'

        logging.info('Reading lexicon from {}'.format(filename))

        # load json if there is one
        if filename.endswith('.json'):
            with open(filename, 'r') as jsonin:
                try:
                    json_repr = json.loads(jsonin.read())
                except json.decoder.JSONDecodeError:
                    logging.error('Json file seems to be broken: {}'.format(filename))
                    raise
            self.language = json_repr['language']
            self._entries = {
                entry: LexiconEntry(
                    json_repr['_entries'][entry]['transcription'],
                    json_repr['_entries'][entry]['generated']
                )
                for entry in json_repr['_entries']
            }
        elif filename.endswith('.pron'):
            self._read_pron(filename)
        elif os.path.basename(filename).startswith('cmu'):
            self._read_pron(filename)

    def extend_lexicon(self, filename):
        progress = Counter('Reading lexicon entries ')
        new_entries = {}
        with open(filename, "r", encoding="ISO-8859-1", errors="ignore") as f:
            for line in f:
                progress.next()
                item = line.strip("\n").split("\t")
                token = item[0]
                if token not in self._entries:
                    new_entries[token] = LexiconEntry(item[1].split(" "), generated=True)
                    # FIXME: For the cmu format, _entries is now a mixture of
                    # cmu (the original entries) and sampa (the generated
                    # entries) formats. We need to add to _entries to compute
                    # and access number_of_consonants when converting to df
                    self._entries[token] = LexiconEntry(item[1].split(" "), generated=True)
        new_data = self._dict_to_dataframe(new_entries)
        self.data = pd.concat([self.data, new_data])

    def convert_to_sampa(self):
        if not self.sampa:
            if 'eng' in self.language:
                self.data['transcription'] = self.data['transcription'].apply(self._cmu_to_sampa)
            elif self.language in ('nor', 'swe'):
                self.data['transcription'] = self.data['transcription'].apply(self._nst_to_sampa)

            self.data['original'] = self.data['transcription']
            self.sampa = True

    def _cmu_to_sampa(self, transcription):
        mapping = self.phonemes.to_sampa()

        sampa = []
        for phoneme in transcription:
            stress = ''
            if phoneme[-1] in ('0', '1', '2'):
                stress = phoneme[-1]
            sampa.append(mapping[phoneme] + stress)
        return sampa

    def _nst_to_sampa(self, transcription):
        mapping = self.phonemes.to_sampa()
        return [mapping.get(p, p) for p in transcription]

    def number_of_consonants(self, word, original):
        if original:
            pron = self._entries[word].original
        else:
            pron = self._entries[word].transcription
        return sum([p in self.phonemes.consonants for p in pron])

    def _read_pron(self, filename, generated=False):
        '''reads into a dictionary'''

        if self.language in ('nor', 'swe'):
            self._read_pron_nst(filename, generated)
        else:
            self._read_pron_cmu(filename, generated)

    def _read_pron_nst(self, filename, generated):
        '''reads into a dictionary
        format:
        NOR / SWE
        0 - orthography corrected
        3 - decomp
        7 - garbage
        8 - domain
        9 - acronym/abbreviation
        10 - expansion (of 9)
        11-26 - phonetic transcription
        27 - automatically generated pronunciation variant
        47 - original orthography
        '''

        progress = Counter('Reading lexicon entries ')
        with open(filename, "r", encoding="ISO-8859-1", errors="ignore") as f:
            for line in f:
                progress.next()
                item = line.strip('\n').split(';')
                token = item[0].lower()
                trans = item[11]  # unsegmented transcription (str)
                trans_list = []   # transcription as list

                while trans:
                    changed = False
                    # segment the transcription based on known phonemes
                    # tmpphonlist = OrderedDict(sorted(self.phonemes.items(), key=lambda t: t[0]))
                    # for phone in reversed(tmpphonlist):
                    for phone in self._phonemes:
                        if trans.startswith(phone):
                            trans_list.append(phone)
                            trans = trans[len(phone):]
                            changed = True
                            break
                    # ...or not found
                    if not changed:
                        # try removing/ignoring the first symbol (=character)
                        trans_list.append(trans[0])
                        trans = trans[1:]

                self._entries[token] = LexiconEntry(trans_list)
        progress.finish()

    def _read_pron_cmu(self, filename, generated):
        '''reads into a dictionary
        format:
        ENG (CMU)
        TOKEN  PHON1 PHON2 ...
        '''
        progress = Counter('Reading lexicon entries ')
        with open(filename, "r", encoding="utf8", errors="ignore") as f:
            for line in f:
                progress.next()
                if not line.startswith(';;;') and '(' not in line:
                    logging.debug('Reading lexicon entry line {}'.format(line))
                    item = line.strip('\n').split(' ')
                    item = [x for x in item if x]  # remove empty elements
                    token = item[0].lower()
                    self._entries[token] = LexiconEntry(item[1:])

        progress.finish()

    def _to_json(self):
        entries = self.data[['transcription', 'generated']]
        parsed = json.loads(entries.to_json(orient='index', indent=2))
        return {
            'language': self.language,
            '_entries': parsed
        }

    def save_to_json_file(self, filename, overwrite=False):
        '''save lexicon transcriptions to json
        - done for any lexicon that is not already in json format
        - if there already is a json, explicit overwriting is required, e.g.
          when extending the lexicon
        :param filename: json path to write to
        :param overwrite: force file writing
        '''
        if not filename.endswith('json') or overwrite:
            if filename.endswith('.pron'):
                filename = filename.replace('.pron', '.json')
            elif os.path.basename(filename).startswith('cmu') and not filename.endswith('json'):
                filename += '.json'

            with open(filename, 'w') as jsonout:
                jsonout.write(json.dumps(self._to_json(), indent=2))
