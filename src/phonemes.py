from abc import ABC, abstractmethod
import pandas as pd
from ipc_features import IPC_ENG, IPC_NOR, IPC_SWE
from wcm_features import WCM_ENG, WCM_NOR, WCM_SWE

'''Phoneme inventories and articulation properties for the used languages

NB: When a lexicon is read and transcriptions are segmented to turn strings
    into lists, phonemes are sorted by length, so they can be specified here in
    any convenient order.
'''


class Phonemes(ABC):

    @abstractmethod
    def __init__(self):
        self.inventory = pd.DataFrame()
        self.consonants = pd.DataFrame()
        self.vowels = pd.DataFrame()
        self.diphthongs = pd.DataFrame()
        self.ipc_features = {}

    @property
    def affricates(self):
        return ("tS", "dZ")

    @property
    def fricatives(self):
        return ("f", "v", "s", "s`", "S", "s'", "T", "D", "z", "Z", "x\\", "h")

    @property
    def liquids(self):
        return ("l", "l`", "r")

    @property
    def nasals(self):
        return ("m", "n", "n`", "N", "n=", "n`=", "N=")

    @property
    def plosives(self):
        return ("p", "t", "t`", "k", "b", "d", "d`", "g")

    @property
    def syllabic(self):
        return ("n=", "N=", "n`=")

    @property
    @abstractmethod
    def _phonemes(self):
        pass

    @property
    @abstractmethod
    def approximants(self):
        pass

    @property
    @abstractmethod
    def glides(self):
        pass

    @property
    def liquidGlides(self):
        return self.liquids + self.glides

    @property
    def obstruents(self):
        return self.plosives + self.fricatives + self.affricates

    @abstractmethod
    def to_sampa(self):
        return dict()

    ########################################
    # IPC computation
    ########################################
    def dorsal_consonant(self, phone):
        return (phone in self.ipc_features
                and self.ipc_features[phone]['ConsPlace'] == 'dorsal')

    def fricative_affricate_liquid_consonant(self, phone):
        return (phone in self.ipc_features
                and (
                  self.ipc_features[phone]['ConsManner'] == 'fricative'
                  or self.ipc_features[phone]['ConsManner'] == 'affricate'
                  or self.ipc_features[phone]['ConsManner'] == 'liquid'
                  )
                )

    def rhotic_vowels(self, _transcription, _vowel_positions):
        return 0

    def score_variegation(self, consonant_list):
        c = 0
        # check ConsPlace variegation
        for i in range(len(consonant_list)-1):
            if (
              consonant_list[i] != "CLUSTER"
              and consonant_list[i+1] != "CLUSTER"
              and self.ipc_features[consonant_list[i]]["ConsPlace"] != self.ipc_features[consonant_list[i+1]]["ConsPlace"]
              ):
                c += 1
        return c

    def number_of_heterorg_clusters(self, clusters):
        c = 0
        for cluster in clusters:
            for i in range(len(cluster)-1):
                if (self.ipc_features[cluster[i]]["ConsPlace"] != self.ipc_features[cluster[i+1]]["ConsPlace"]):
                    c += 1
                    break
        return c

    ########################################
    # WCM computation
    ########################################
    def velar_consonant(self, phone):
        return (phone in self.wcm_features
                and self.wcm_features[phone]['ConsPlace'] == 'velar')

    def liquid_or_rhotic_consonant(self, phone):
        return (phone in self.wcm_features
                and (self.wcm_features[phone]["ConsManner"] == "liquid"
                     or self.wcm_features[phone]["ConsManner"] == "rhotic"
                     )
                )

    def r_consonant(self, phone):
        return False

    def fricative_or_affricate_consonant(self, phone):
        return (phone in self.wcm_features
                and (self.wcm_features[phone]["ConsManner"] == "fricative"
                     or self.wcm_features[phone]["ConsManner"] == "affricate"
                     )
                )

    def voiced_fricative(self, phone):
        return (phone in self.wcm_features
                and self.wcm_features[phone]["ConsManner"] == "fricative"
                and self.wcm_features[phone]["ConsVoicing"] == "voiced"
                )

    def long_front_rounded_vowel(self, phone):
        return (phone in self.wcm_features
                and self.wcm_features[phone]["VowLength"] == "long"
                and self.wcm_features[phone]["VowFrontBack"] == "front"
                and self.wcm_features[phone]["VowRounding"] == "rounded"
                )


class SwedishPhonemes(Phonemes):
    _phonemes = {
        'v': [
            "2:", "9", "E:", "A:", "E", "I", "O", "Y", "U",
            "a", "e:", "e", "i:", "o:", "u0",
            # also: non-sampa (NSTlex) symbols
            "8", "u:", "y:", "}:"
            ],
        'd': [
            "EU", "aU", "E*U", "a*U"
            ],
        'c': [
            "N", "b", "d`", "d", "f", "g", "h", "j", "k",
            "l`", "l", "m", "n`", "n", "p", "r", "s'",
            # also: non-sampa (NSTlex) symbols
            "s`", "C", "s", "t`", "t", "v", "x\\"
            ]
        }

    approximants = ("l", "l`", "r")
    glides = tuple()

    def __init__(self, ipc_file=None):
        self.ipc_features = IPC_SWE
        self.wcm_features = WCM_SWE
        self.ipc_to_sampa()
        self.inventory = pd.DataFrame.from_records(
            [(phon, t) for t in SwedishPhonemes._phonemes for phon in SwedishPhonemes._phonemes[t]],
            columns=['phoneme', 'phoneme_type']
        )
        self.consonants = self.inventory.where(self.inventory['phoneme_type'] == 'c')
        self.consonants = [p for p in self.consonants['phoneme'].tolist() if isinstance(p, str)]

        self.vowels = self.inventory.where(self.inventory['phoneme_type'] == 'v')
        self.diphthongs = self.inventory.where(self.inventory['phoneme_type'] == 'd')
        self.vowels = self.vowels.dropna()
        self.diphthongs = self.diphthongs.dropna()

    def to_sampa(self):
        return {
            'E*U': 'EU',
            'a*U': 'aU',
            "s'": 'C',
            'u0': '8'
        }

    def ipc_to_sampa(self):
        ipc_sampa_features = {}
        for phone, features in self.ipc_features.items():
            add_entry = self.to_sampa().get(phone)
            if add_entry:
                ipc_sampa_features[add_entry] = features
            ipc_sampa_features[phone] = features
        self.ipc_features = ipc_sampa_features

    def r_consonant(self, phone):
        return phone == 'r'


class NorwegianPhonemes(Phonemes):
    _phonemes = {
        'v': [
            "2:", "9", "@", "A:", "A", "I", "O", "U", "Y",
            "e:", "i:", "o:", "}:", "u:", "u0", "y:", "{:",
            "{", "}", "E"
            ],
        'd': [
            "9Y", "9*Y", "A*I", "AI", "E*u0", "E}",
            "O*Y", "OY", "{*I", "{I"
            ],
        'c': [
            "C", "N=", "N", "S", "b", "d`", "d",
            "f", "g", "h", "j", "k", "l", "l`=",
            "l`", "l=", "m", "n`", "n`=", "n=", "n",
            "p", "r", "s`", "s", "tS", "t`", "t",
            "v"
            ]
        }

    approximants = ("l", "l`", "r")
    glides = tuple()

    def __init__(self, ipc_file=None):
        self.ipc_features = IPC_NOR
        self.wcm_features = WCM_NOR
        self.inventory = pd.DataFrame.from_records(
            [(phon, t) for t in NorwegianPhonemes._phonemes for phon in NorwegianPhonemes._phonemes[t]],
            columns=['phoneme', 'phoneme_type']
        )
        self.consonants = self.inventory.where(self.inventory['phoneme_type'] == 'c')
        self.consonants = [p for p in self.consonants['phoneme'].tolist() if isinstance(p, str)]

        self.vowels = self.inventory.where(self.inventory['phoneme_type'] == 'v')
        self.diphthongs = self.inventory.where(self.inventory['phoneme_type'] == 'd')

        self.vowels = self.vowels.dropna()
        self.diphthongs = self.diphthongs.dropna()

    def to_sampa(self):
        return {
            '9*Y': '9Y',
            'A*I': 'AI',
            'O*Y': 'OY',
            'u0': '}',
            '{*I': '{I',
            'E*u0': 'E}'
        }

    def r_consonant(self, phone):
        return phone == 'r'


class EnglishPhonemes(Phonemes):
    _phonemes = {
        'v': [
            "A:", "{", "@", "V", "O:", "E", "3:",
            "I", "i:", "U", "u:"
            ],
        'd': [
            "aU", "aI", "eI", "oU", "OI"
            ],
        'c': [
            "b", "tS", "d", "D", "f", "g", "h", "dZ",
            "k", "l", "m", "n", "N", "p", "r", "s",
            "S", "t", "T", "v", "w", "j", "z", "Z"
            ]
        }

    approximants = ("j", "w", "l", "r")
    glides = ("j", "w")

    def __init__(self, ipc_file=None):
        self.ipc_features = IPC_ENG
        self.wcm_features = WCM_ENG
        self.inventory = pd.DataFrame.from_records(
            [(phon, t) for t in EnglishPhonemes._phonemes for phon in EnglishPhonemes._phonemes[t]],
            columns=['phoneme', 'phoneme_type']
        )
        self.consonants = self.inventory.where(self.inventory['phoneme_type'] == 'c')
        self.consonants = [p for p in self.consonants['phoneme'].tolist() if isinstance(p, str)]

        self.vowels = self.inventory.where(self.inventory['phoneme_type'] == 'v')
        self.diphthongs = self.inventory.where(self.inventory['phoneme_type'] == 'd')

        self.vowels = self.vowels.dropna()
        self.diphthongs = self.diphthongs.dropna()

    def to_sampa(self):
        return {
            '$': '$',
            'AA0': 'A:',
            'AA1': 'A:',
            'AA2': 'A:',
            'AE0': '{',
            'AE1': '{',
            'AE2': '{',
            'AH0': '@',
            'AH1': 'V',
            'AH2': 'V',
            'AO0': 'O:',
            'AO1': 'O:',
            'AO2': 'O:',
            'AW0': 'aU',
            'AW1': 'aU',
            'AW2': 'aU',
            'AY0': 'aI',
            'AY1': 'aI',
            'AY2': 'aI',
            'EH0': 'E',
            'EH1': 'E',
            'EH2': 'E',
            'ER0': '3:',
            'ER1': '3:',
            'ER2': '3:',
            'EY0': 'eI',
            'EY1': 'eI',
            'EY2': 'eI',
            'IH0': 'I',
            'IH1': 'I',
            'IH2': 'I',
            'IY0': 'i:',
            'IY1': 'i:',
            'IY2': 'i:',
            'OW0': 'oU',
            'OW1': 'oU',
            'OW2': 'oU',
            'OY0': 'OI',
            'OY1': 'OI',
            'OY2': 'OI',
            'UH0': 'U',
            'UH1': 'U',
            'UH2': 'U',
            'UW0': 'u:',
            'UW1': 'u:',
            'UW2': 'u:',
            'B': 'b',
            'CH': 'tS',
            'D': 'd',
            'DH': 'D',
            'F': 'f',
            'G': 'g',
            'HH': 'h',
            'JH': 'dZ',
            'K': 'k',
            'L': 'l',
            'M': 'm',
            'N': 'n',
            'NG': 'N',
            'P': 'p',
            'R': 'r',
            'S': 's',
            'SH': 'S',
            'T': 't',
            'TH': 'T',
            'V': 'v',
            'W': 'w',
            'Y': 'j',
            'Z': 'z',
            'ZH': 'Z'
        }

    def rhotic_vowels(self, transcription, vowel_positions):
        # ENG: check if vowel followed by /r/
        c = 0
        for pos in vowel_positions:
            vowel = transcription[pos]
            if (
              pos < len(transcription) - 1
              and (vowel.startswith("A:")
                   or vowel.startswith("E")
                   or vowel.startswith("I")
                   or vowel.startswith("U")
                   )
              and transcription[pos+1] == "r"
              ):
                c += 1
        return c
