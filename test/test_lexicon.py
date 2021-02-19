import sys
sys.path.append('src')

from lexicon import Lexicon


def read_lexicon(language):
    lex = {
        'eng': 'test/static/eng_test_lexicon.pron',
        'nor': 'test/static/nor_test_lexicon.pron',
        'swe': 'test/static/swe_test_lexicon.pron',
    }
    return Lexicon(language, lex[language], from_original=True)


def test_len_swe_lexicon():
    lexicon = read_lexicon('swe')
    assert len(lexicon) == 100


def test_entry_swe_lexicon():
    lexicon = read_lexicon('swe')
    assert lexicon['-tals']['transcription'] == ['"', 't', 'A:', 'l', 's']


def test_extend_swe_lexicon():
    lexicon = read_lexicon('swe')
    lexicon.extend_lexicon('test/static/swe_additional_transcriptions.lex')
    assert len(lexicon) == 110


def test_len_nor_lexicon():
    lexicon = read_lexicon('nor')
    assert len(lexicon) == 77


def test_entry_nor_lexicon():
    lexicon = read_lexicon('nor')
    assert lexicon['-aktere']['transcription'] == ['"', 'A', 'k', '$', 't', '@', '$', 'r', '@']


def test_len_eng_lexicon():
    lexicon = read_lexicon('eng')
    assert len(lexicon) == 37


def test_entry_eng_lexicon():
    lexicon = read_lexicon('eng')
    assert lexicon["'twas"]['transcription'] == ['t', 'w', 'V1', 'z']
