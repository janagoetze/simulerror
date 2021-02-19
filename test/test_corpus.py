import sys
sys.path.append('src')

from corpus import Corpus


def read_corpora(corpora):
    return Corpus(corpora)


def test_entries_och():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['och'] == 3535


def test_entries_det():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['det'] == 2862


def test_entries_hon():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['hon'] == 2221


def test_entries_i():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['i'] == 2085


def test_entries_ar():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['är'] == 2039


def test_entries_pa():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['på'] == 1921


def test_entries_att():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['att'] == 1849


def test_entries_sager():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['säger'] == 1565


def test_entries_han():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['han'] == 1558


def test_entries_inte():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq'])
    assert corpus['inte'] == 1483


def test_len_corpus():
    corpus = read_corpora(['test/static/swe_test_corpus_2.freq'])
    assert len(corpus) == 50


def test_total_entries_same():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_2.freq'])
    assert len(corpus) == 50


def test_total_entries_different():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_4.freq'])
    assert len(corpus) == 20


def test_len_corpus_files():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_2.freq'])
    assert len(corpus._corpora) == 2


def test_add_to_counts():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_2.freq'])
    assert corpus['att'] == 3698


def test_del_instances():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_2.freq'])
    assert corpus.del_instances == 0


def test_del_entries():
    corpus = read_corpora(['test/static/swe_test_corpus_1.freq',
                           'test/static/swe_test_corpus_2.freq'])
    assert corpus.del_entries == 0
