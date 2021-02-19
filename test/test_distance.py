import sys
sys.path.append('src')

from measures import Distance


def initialize_dist(csvfile, phonfreq, language):
    return Distance(csvfile, phonfreq, language)


def test_distance_ipc_stopping_swe_spoket():
    dist = initialize_dist(
        'test/static/swe_simulation_stopping.csv',
        'test/static/swe.phone.freq',
        'swe'
    )

    input = ['""', '""', 's', 'p', '2:', '$', 'k', 'e', 't']
    output = ['""', '""', 'p', '2:', '$', 'k', 'e', 't']
    assert dist._calculate_ipc('spöket', output, input) == -2


def test_distance_wcm_stopping_swe_spoket():
    dist = initialize_dist(
        'test/static/swe_simulation_stopping.csv',
        'test/static/swe.phone.freq',
        'swe'
    )

    dist.measure('wcm')
    spoket_index = dist.simulation.index[dist.simulation['token'] == 'spöket']
    spoket_index = spoket_index.to_list()[0]
    assert dist.simulation.at[spoket_index, 'wcm'] == -2


def test_distance_pcc_stopping_swe_spoket():
    dist = initialize_dist(
        'test/static/swe_simulation_stopping.csv',
        'test/static/swe.phone.freq',
        'swe'
    )

    dist.measure('pcc')
    spoket_index = dist.simulation.index[dist.simulation['token'] == 'spöket']
    spoket_index = spoket_index.to_list()[0]
    assert dist.simulation.at[spoket_index, 'pcc'] == 0.75


def test_distance_pwp_stopping_swe_spoket():
    dist = initialize_dist(
        'test/static/swe_simulation_stopping.csv',
        'test/static/swe.phone.freq',
        'swe'
    )

    dist.measure('pwp')
    spoket_index = dist.simulation.index[dist.simulation['token'] == 'spöket']
    spoket_index = spoket_index.to_list()[0]
    assert dist.simulation.at[spoket_index, 'pwp'] == 0.8


def test_distance_pcc_coronal_backing_swe():
    dist = initialize_dist(
        'test/static/swe_simulation_coronal_backing.csv',
        'test/static/swe.phone.freq',
        'swe'
    )
    assert dist.measure('pcc') == {
        'pcc_on_types': {
            'N': 940,
            'mean': 0.7145896656534954,
            'stdev': 0.2830373594670498,
            'quantiles': [0.5, 0.75, 1.0]
        },
        'pcc_on_tokens': {
            'N': 73585,
            'mean': 0.686500257234033,
            'stdev': 0.3530450180715217,
            'quantiles': [0.5, 0.75, 1.0]
        }
    }


def test_distance_pcc_stopping_swe_total():
    dist = initialize_dist(
        'test/static/swe_simulation_stopping.csv',
        'test/static/swe.phone.freq',
        'swe'
    )
    assert dist.measure('pcc') == {
        'pcc_on_types': {
            'N': 940,
            'mean': 0.8149341438703126,
            'stdev': 0.2225714694654535,
            'quantiles': [0.6666666666666666, 1.0, 1.0]
        },
        'pcc_on_tokens': {
            'N': 73585,
            'mean': 0.8485251587893464,
            'stdev': 0.24291991046026334,
            'quantiles': [0.6666666666666666, 1.0, 1.0]
        }
    }


def test_distance_pcc_coronal_backing_nor():
    dist = initialize_dist(
        'test/static/nor_simulation_coronal_backing.csv',
        'test/static/nor.phone.freq',
        'nor'
    )
    assert dist.measure('pcc') == {
        'pcc_on_types': {
            'N': 2490,
            'mean': 0.7318773506725322,
            'stdev': 0.28617824677369147,
            'quantiles': [0.5, 0.75, 1.0]
        },
        'pcc_on_tokens': {
            'N': 42420,
            'mean': 0.7331594953713299,
            'stdev': 0.37657283117214996,
            'quantiles': [0.5, 1.0, 1.0]
        }
    }


def test_distance_pcc_stopping_nor():
    dist = initialize_dist(
        'test/static/nor_simulation_stopping.csv',
        'test/static/nor.phone.freq',
        'nor'
    )
    assert dist.measure('pcc') == {
        'pcc_on_types': {
            'N': 2490,
            'mean': 0.8194097023012716,
            'stdev': 0.2360910274835278,
            'quantiles': [0.6666666666666666, 1.0, 1.0]
        },
        'pcc_on_tokens': {
            'N': 42420,
            'mean': 0.890083191142214,
            'stdev': 0.24317917170530978,
            'quantiles': [1.0, 1.0, 1.0]
        }
    }
