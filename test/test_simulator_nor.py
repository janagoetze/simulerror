import sys
sys.path.append('src')
from simulator import Simulator
from patterns import CORONAL_BACKING, R_WEAKENING, STOPPING, VELAR_FRONTING


def initialize_sim(corpora=[]):
    if not corpora:
        corpora = ['test/static/nor_test_corpus.freq']
    return Simulator('nor', 'test/static/nor_test_lexicon_large.pron', corpora)


def test_simulator_nor_coronal_backing_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(CORONAL_BACKING) == {
        'count_affected_words': 9,
        'count_words': 12,
        'changed_consonants': 12,
        'num_consonants_changed': 107
    }


def test_simulator_nor_velar_fronting_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(VELAR_FRONTING) == {
        'count_affected_words': 1,
        'count_words': 1,
        'changed_consonants': 1,
        'num_consonants_changed': 4
    }


def test_simulator_nor_r_weakening_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(R_WEAKENING) == {
        'count_affected_words': 4,
        'count_words': 4,
        'changed_consonants': 4,
        'num_consonants_changed': 39
    }


def test_simulator_nor_cluster_reduction_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._cluster_reduction() == {
        'count_affected_words': 2,
        'count_words': 2,
        'changed_consonants': 2,
        'num_consonants_changed': 31
    }


def test_simulator_nor_pretonic_syllable_deletion_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._pretonic_syllable_deletion() == {
        'count_affected_words': 2,
        'count_words': 2,
        'changed_consonants': 2,
        'num_consonants_changed': 31
    }


def test_simulator_nor_stopping_changelog():
    sim = initialize_sim(['test/static/nor_test_corpus.2.freq'])
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(STOPPING) == {
        'count_affected_words': 4,
        'count_words': 6,
        'changed_consonants': 6,
        'num_consonants_changed': 10330
    }


def test_simulator_nor_coronal_backing_num_of_consonants():
    sim = initialize_sim()
    sim.simulate('coronal_backing')
    assert sim._num_consonants_changed == 107


def test_simulator_nor_velar_fronting_num_of_consonants():
    sim = initialize_sim()
    sim.simulate('velar_fronting')
    assert sim._num_consonants_changed == 4


def test_simulator_nor_stopping_num_of_consonants():
    sim = initialize_sim(['test/static/nor_test_corpus.2.freq'])
    sim.simulate('stopping')
    assert sim._num_consonants_changed == 10330
