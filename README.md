# simulerror

This code provides functionality to simulate the speech error patterns that were investigated in

> STRÖMBERGSSON, S., GÖTZE, J., EDLUND, J., & NILSSON BJÖRKENSTAM, K. (to appear). Simulating speech error patterns across languages and different datasets. Language and Speech.

 It also includes some of the complexity measures that were used for quantifying error impact.

The implemented speech error patterns are (see also Section [Implemented error patterns](#implemented-error-patterns) below):

- Velar fronting
- Coronal backing
- Stopping
- r weakening
- Cluster reduction
- Delete pretonic syllable


# Installation & Usage

Recommended: create a virtual environment:
```bash
python -m venv env && . env/bin/activate
```

Required: Python 3.8+. The code was developed and tested under Python 3.8.3.

Required packages can be installed using pip:
```bash
pip install -r requirements.txt
```

For running tests, type `pytest`.

## Usage details

In order to run a simulation, you can call the [commandline scripts](#using-the-commandline-scripts-to-run-simulations) as shown in the examples below, or use the implementation as a [library](#using-the-implementation-as-a-library-in-your-python-code).

NB: The first time a simulation is run for any language, the lexicon is converted into a json format. This step takes some time. In subsequent calls, the information is read from json and the processing is (much) faster.

### Using the commandline scripts to run simulations
In order to run a simulation, you can call the commandline scripts `simulate.py` and `calculate_distance.py` as shown in the examples below.

`simulate.py` needs the correct lexicon, corpus, and the language, as well as the error pattern you want to apply. You can call the script with several frequency lists, they will be combined into one corpus. The language parameter selects the correct phonemic inventory and lexicon: specify the lexicon by adjusting the path in config.json. If you need to adjust the inventory or add a new language, this can be done in `phonemes.py`

`calculate_distance.py` needs the simulation output, the language for selecting the correct phonemic inventory, and all measures to be computed.

The below calls are examples. You will need to adjust the paths according to your directory structure. For details on the required formats, see Section [Resources and Data](#resources-and-data) below.

### Simulate stopping in Swedish using one frequency list

```bash
python simulate.py -e stopping -l swe -c corpus.freq -o analysis_results
```

This will create a file analysis_results/stopping.csv.

### Simulate coronal_backing in Swedish using two frequency lists

```bash
python simulate.py -e stopping -l swe -c corpus.1.freq -c corpus.2.freq
```

### Compute PPC and IPC
```bash
python calculate_distance.py -d pcc -d ipc -l swe -i analysis_results/stopping.csv
```

This will create a file analysis_results/result.csv.


## Using the implementation as a library in your python code

Alternatively, you can import the classes into your code:

```python
from simulator import Simulator

# initializing the simulator with the language, lexicon and corpora
simulator = Simulator('swe', 'swe_lexicon.json', ['corpus_file_1.txt', 'corpus_file_2.txt'])

# calculating phone frequencies
simulator.token_to_phonfreq_unigram('phone_frequency.txt')
# simulate stopping and backing
simulator.simulate('stopping')
# write result to csv file (measures can then be computed based on this file)
simulator.to_csv('stopping.csv')
```

```python
from measures import Distance

# initializing the Distance object with the input csv, phone frequencies, language, and stopword list
distance = Distance('stopping.csv', 'phone_frequency.txt', 'swe', 'stopwords_swe.txt')

# specify the error pattern column to run measures on
# NB: this allows you to pass a file that was created elsewhere and has several columns for different simulations

result = distance.measure('stopping')
print(result)  # json formatted result

# write object to csv file
distance.to_csv('result_stopping.csv')

```

# Resources and data

In order to run the simulations, you need the following resources:

* a lexicon file, specifying phonemic transcriptions for your language
* a frequency list for your language
  - frequency lists must have the format
    ``frequency\ttoken``, e.g.

    ```
    3535	och
    2862	det
    2221	hon
    2085	i
    2039	är
    1921	på
    1849	att
    1565	säger
    1558	han
    1483	inte
    ```

## Downloading the paper resources

In order to download the resource files used in the paper, run:

`sh scripts/download_data.sh`

This will create a directory `RESOURCES` containing the lexicon files for English, Norwegian, and Swedish:

* `RESOURCES/Lexica/cmudict-0.7b`
* `RESOURCES/Lexica/nor030224NST.pron`
* `RESOURCES/Lexica/swe030224NST.pron`

Alternatively, you can copy the urls from `scripts/download_data.sh` and use your browser to obtain them. You can then manually create a `RESOURCES` directory, which is where the scripts expect the resource files to live in. If you want to keep your lexica in a different directory, adjust the config.json accordingly.

Note that all of the above lexica are converted to a json format when they are first read (and saved in the same directory). This conversion can take considerable time. Once the lexicon in json format, subsequent reading is fast.

### Extending the lexicon

The default lexicon for a language is read from config.json. The lexicon can be
extended with entries by supplying one or more files that list transcriptions in
 the format `token\ttranscription`, where transcription is a space-separated
 list of phonemes, for example:
```
den d e n
dä  " d E:
på  " p o:
där d E: r
hä  " " h E:
```

An existing lexicon can be extended by calling the following script with as
many `-t` parameters as necessary:
```bash
python src/prepare_lexicon.py -l swe -o path_to_new_lexicon.json -t path_to_new_transcriptions
```

Entries that are added are labeled as being generated entries. Existing entries
will not be over-written. In order to use this new json lexicon, adjust the path
specification in config.json.


## Implemented error patterns

### Velar fronting (`velar_fronting`)

- /k/->/t/
- /g/->/d/
- /N/->/n/

### Coronal backing (`coronal_backing`)

- /t/->/k/
- /d/->/g/
- /n/->/N/ (+ retroflexes)

### Stopping (`stopping`)

- /f/->/p/
- /v/->/b/
- /s/->/t/
- /S/->/t/
- /s\`/->/t\`/
- /s'/->/t/
- /x\/->/k/
- /tS/->/t/
- /z/->/d/
- /Z/->/d/
- /dZ/->/d/
- /T/->/p/
- /D/->/b/

### r weakening (`r_weakening`)

- /r/->/j/

### Cluster reduction (`cluster_reduction`)

- /Obstr + Approx/ -> /Obstr/
- /s/ + Plosive -> Plosive
- /s/ + Nasal -> Nasal
- /s/ + Liquid -> /s/
- /s/ + Approx -> /s/
- Fric + Liquid/Glide -> Fric
- /s/ + Plos + Approx -> Plos


### Pretonic syllable deletion (`pretonic_syllable_deletion`)

- (C\*VC\*) + 'C\*VC\* -> 'C\*VC\*


## Implemented distance measures

- PCC: Percentage Consonants Correct (`-d pcc`)
- IPC: Index of Phonetic Complexity (`-d ipc`)
- WCM: Word Complexity Measure (`-d wcm`)
- PWP: Proportion of Whole-Word Proximity (`-d pwp`)


# Citation

To cite the simulerror tools in publications, please use:

> STRÖMBERGSSON, S., GÖTZE, J., EDLUND, J., & NILSSON BJÖRKENSTAM, K. (to appear). *Simulating speech error patterns across languages and different datasets*. Language and Speech.
