import sys
sys.path.append('src')
from simulator import Simulator
from patterns import CORONAL_BACKING, R_WEAKENING, STOPPING, VELAR_FRONTING


def initialize_sim(lexicon, corpora):
    return Simulator('swe', lexicon, corpora)


def test_simulator_swe_replace_sound_replace():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulated, _count = sim._replace_sound(['a', 't', 'a', 'r'], 't', 'k', True)
    assert simulated == ['a', 'k', 'a', 'r']


def test_simulator_swe_replace_sound_do_not_replace():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulated, _count = sim._replace_sound(['l', 'i:', 'k', 't'], 't', 'k', True)
    assert simulated == ['l', 'i:', 'k']


def test_simulator_swe_coronal_backing_adventures():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'adventures'
    column = 'coronal_backing'
    input = ['{', 'g', '$', '"', 'v', 'E', 'N', '$', 't', 'S', '3:', 'z']
    output = ['{', 'g', '$', '"', 'v', 'E', 'N', '$', 'k', 'S', '3:', 'z']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']
    simulated = input
    for sound in CORONAL_BACKING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, CORONAL_BACKING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_coronal_backing_kanner():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'kanner'
    column = 'coronal_backing'
    input = ["\"", "s'", "E", "$", "n", "e", "r"]
    output = ["\"", "s'", "E", "$", "N", "e", "r"]
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']
    simulated = input
    for sound in CORONAL_BACKING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, CORONAL_BACKING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_skull():

    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'skull'
    column = 'stopping'
    input = ['"', 's', 'k', 'u', '0', 'l']
    output = ['"', 'k', 'u', '0', 'l']
    sim.simulation['transcription'] = sim.simulation['transcription'].astype(object)
    sim.simulation.at[simulate, 'transcription'] = input
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_kokskap():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'kökskåp'
    column = 'stopping'
    input = ['"', '"', "s'", '9', 'k', 's', '$', '%', 's', 'k', 'o:', 'p']
    output = ['"', '"', 't', '9', 'k', 't', '$', '%', 'k', 'o:', 'p']
    sim.simulation.loc[simulate] = {'transcription': input, 'frequency': 0}
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_kants():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'känts'
    column = 'stopping'
    input = ['"', "s'", 'e', 'n', 't', 's']
    output = ['"', 't', 'e', 'n', 't']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_sen():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'sen'
    column = 'stopping'
    input = ['"', 's', 'e:', 'n']
    output = ['"', 't', 'e:', 'n']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_sitta():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'sitta'
    column = 'stopping'
    input = ['"', '"', 's', 'I', '$', 't', 'a']
    output = ['"', '"', 't', 'I', '$', 't', 'a']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_dessa():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'dessa'
    column = 'stopping'

    input = ['"', '"', 'd', 'E', '$', 's', 'a']
    output = ['"', '"', 'd', 'E', '$', 't', 'a']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_stopping_stranden():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'stranden'
    column = 'stopping'
    input = ['s', 't', 'r', 'a', 'n', 'd', 'e', 'n']
    output = ['t', 'r', 'a', 'n', 'd', 'e', 'n']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    for sound in STOPPING:
        is_consonant = sound in sim.lexicon.phonemes.consonants
        simulated, _count = sim._replace_sound_by_row(simulated, sound, STOPPING[sound], is_consonant)
    assert simulated == output


def test_simulator_swe_coronal_backing_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(CORONAL_BACKING) == {
        'count_affected_words': 5,
        'count_words': 5,
        'changed_consonants': 6,
        'num_consonants_changed': 166
    }


def test_simulator_swe_cluster_reduction_():

    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'skull'
    column = 'cluster_reduction'
    input = ['"', 's', 'k', 'u', '0', 'l']
    output = ['"', 'k', 'u', '0', 'l']
    sim.simulation['transcription'] = sim.simulation['transcription'].astype(object)
    sim.simulation.at[simulate, 'transcription'] = input
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    simulated, _count = sim._reduce_cluster(simulated)
    assert simulated == output


def test_simulator_swe_stopping_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(STOPPING) == {
        'count_affected_words': 4,
        'count_words': 5,
        'changed_consonants': 5,
        'num_consonants_changed': 816
    }


def test_simulator_swe_velar_fronting_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(VELAR_FRONTING) == {
        'count_affected_words': 3,
        'count_words': 3,
        'changed_consonants': 3,
        'num_consonants_changed': 69
    }


def test_simulator_swe_r_weakening_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._replace_sounds(R_WEAKENING) == {
        'count_affected_words': 3,
        'count_words': 3,
        'changed_consonants': 3,
        'num_consonants_changed': 428
    }


def test_simulator_swe_cluster_reduction_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._cluster_reduction() == {
        'count_affected_words': 1,
        'count_words': 1,
        'changed_consonants': 1,
        'num_consonants_changed': 16
    }


# FIXME: choose different corpus to get non-zero result
def test_simulator_swe_pretonic_syllable_deletion_changelog():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulation['simulation'] = sim.simulation['transcription']
    assert sim._pretonic_syllable_deletion() == {
        'count_affected_words': 0,
        'count_words': 0,
        'changed_consonants': 0,
        'num_consonants_changed': 0
    }


def test_simulator_swe_coronal_backing_num_of_consonants():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulate('coronal_backing')
    assert sim._num_consonants_changed == 166


def test_simulator_swe_velar_fronting_num_of_consonants():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulate('velar_fronting')
    assert sim._num_consonants_changed == 69


def test_simulator_swe_stopping_num_of_consonants():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    sim.simulate('stopping')
    assert sim._num_consonants_changed == 816


def test_simulator_swe_delete_unstressed_inbetween_leverpastej():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'leverpastej'
    column = 'pretonic_syllable_deletion'

    input = ['"', '"', 'l', 'e:', '$', 'v', 'e', '$', 'p', 'a', '$', '%', 's', 't', 'e', 'j']
    output = ['"', '"', 'l', 'e:', '$', 'v', 'e', '$', '%', 's', 't', 'e', 'j']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    simulated, _count = sim._delete_unstressed_inbetween(simulated)
    assert simulated == output


def test_simulator_swe_delete_unstressed_inbetween_vakskabinett():
    sim = initialize_sim(
        'test/static/swe_test_lexicon_large.pron',
        ['test/static/swe_test_corpus_3.freq']
    )
    simulate = 'leverpastej'
    column = 'pretonic_syllable_deletion'

    input = ['"', '"', 'v', 'a', 'k', 's', '$', 'k', 'a', '$', 'b', 'I', '$', '%', 'n', 'e', 't']
    output = ['"', '"', 'v', 'a', 'k', 's', '$', 'k', 'a', '$', '%', 'n', 'e', 't']
    sim.simulation.loc[simulate] = {
        'transcription': input,
        'frequency': 0,
        'original': [],
        'generated': False,
        'changed_consonants': 0,
        'changes': [],
        'num_C_original': 0
    }
    sim.simulation[column] = sim.simulation['transcription']

    simulated = input
    simulated, _count = sim._delete_unstressed_inbetween(simulated)
    assert simulated == output
