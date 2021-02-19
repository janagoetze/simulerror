import sys
sys.path.append('src')
from simulator import Simulator
from patterns import CORONAL_BACKING, R_WEAKENING, STOPPING, VELAR_FRONTING


def initialize_sim(corpora=[]):
    if not corpora:
        corpora = ['test/static/eng_test_corpus.freq']
    return Simulator('eng', 'test/static/cmu_eng_test_lexicon_large', corpora)


def test_simulator_eng_coronal_backing_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(CORONAL_BACKING) == {
        'count_affected_words': 22,
        'count_words': 25,
        'changed_consonants': 25,
        'num_consonants_changed': 96690
    }


def test_simulator_eng_velar_fronting_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(VELAR_FRONTING) == {
        'count_affected_words': 4,
        'count_words': 4,
        'changed_consonants': 4,
        'num_consonants_changed': 4976
    }


def test_simulator_eng_r_weakening_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(R_WEAKENING) == {
        'count_affected_words': 5,
        'count_words': 5,
        'changed_consonants': 5,
        'num_consonants_changed': 2033
    }


def test_simulator_eng_cluster_reduction_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._cluster_reduction() == {
        'count_affected_words': 3,
        'count_words': 3,
        'changed_consonants': 3,
        'num_consonants_changed': 803
    }


# FIXME: choose different corpus to get non-zero result
def test_simulator_eng_pretonic_syllable_deletion_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._pretonic_syllable_deletion() == {
        'count_affected_words': 0,
        'count_words': 0,
        'changed_consonants': 0,
        'num_consonants_changed': 0
    }


def test_simulator_eng_stopping_changelog():
    sim = initialize_sim()
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(STOPPING) == {
        'count_affected_words': 10,
        'count_words': 10,
        'changed_consonants': 10,
        'num_consonants_changed': 9853
    }


def test_simulator_eng_coronal_backing_num_of_consonants():
    sim = initialize_sim()
    sim.simulate('coronal_backing')
    assert sim._num_consonants_changed == 96690


def test_simulator_eng_velar_fronting_num_of_consonants():
    sim = initialize_sim()
    sim.simulate('velar_fronting')
    assert sim._num_consonants_changed == 4976


def test_simulator_eng_stopping_num_of_consonants():
    sim = initialize_sim()
    sim.simulate('stopping')
    assert sim._num_consonants_changed == 9853
