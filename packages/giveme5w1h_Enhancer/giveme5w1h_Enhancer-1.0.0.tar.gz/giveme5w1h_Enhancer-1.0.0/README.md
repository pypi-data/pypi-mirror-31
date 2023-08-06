# Giveme5W_NewsCluster_enhancer

* Enhancer can perform further feature extraction and/or selection.
* Sourcecode of all enhancer is saved under /codebase/ to ensure results are reproachable at any time.


## Getting started
Make sure to setup GiveMe5W correct to resolve the modules.
This can be done over PYTHONPATH or any IDE.

### PyCharm
![Project Dependencies](https://github.com/fhamborg/Giveme5W_NewsCluster_enhancer/raw/master/docs/setup/setuppycharm.png)

## AIDA
Aida is available as webservice or can be installed local.
Because of the complex installation and size; online service is set up as default.

### Online Service
Service is limited to 1000 request per day.
You can find details [here](https://www.ambiverse.com/pricing/)

### Local Installation
> AIDA repo went offline, check /codebase/ for the last version

* Source-Download [3.0.4](https://github.com/yago-naga/aida/archive/3.0.4.zip)
* copy sample_settings into settings
* open settings/aida.properties set
  * dataAccess = dmap
* create in settings a file 'dmap_aida.properties', set
  * mapsToLoad = all
  * default.preloadKeys = true
  * default.preloadValues = true


* Data-Download [DMaps](http://resources.mpi-inf.mpg.de/yago-naga/aida/download/entity-repository/AIDA_entity_repository_2014-01-02v10_dmap.tar.bz2)
  * Check also [here](http://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/aida/downloads/) for update
* Decompress the bz2 file
  * use pbzip2 on osx/linux for fast decompression
* create a folder 'dMaps' in the AIDA root directory
  * Unpack the tar file into the dMaps folder
* run
  * mvn package -Dmaven.test.skip=true

> * Warning database dump has 20GB
  * Your computer should have at least 15GB ram

Use environment_enhancer.py to startup CoreNLP and AIDA together.

usage:
```python
from Giveme5W_enhancer.aida import Aida
extractor = FiveWExtractor(extractors=[
        environment_extractor.EnvironmentExtractor(),
    ], enhancement=[
        Aida('when', 'http://myOptionalAidaServer:8080')
    ])
```

## Heideltime
[Heideltime](https://github.com/HeidelTime/heideltime) works out of the box with the 'Giveme5W-runtime-resources'.
This enhancement parse further the "when" answers to get precise time definitions.

- Download [2.2.1](https://github.com/HeidelTime/heideltime/releases/download/VERSION2.2.1/heideltime-standalone-2.2.1.zip)
- Copy it to Giveme5W-runtime-resources
- Follow the installation instruction Manual.pdf
> You must use treeTagger, Heideltime is not compatible with CoreNLP 3.X
> Input files must have a publish date
> Heideltime Candidates can be appended to multiple tokens within one candidate. Heideltime can splits in other, usually wider tokens than coreNLP.

# Usage
```python
from Giveme5W_enhancer.heideltime import Heideltime
extractor = FiveWExtractor(extractors=[
        environment_extractor.EnvironmentExtractor(),
    ], enhancement=[
        Heideltime('when')
    ])
```

The enhancement is stored per candidate, a published date is mandatory for news to resolve relative times.
Example: gold_standard; '071e141c216547f83e2b50a63a728163fa9527e337032e9eb84882d6'
```json
"when": {
      "annotated": [
        {
          "text": "at around 6am"
        }
      ],
      "label": "when",
      "extracted": [
        {
          "parts": [
            [
              {
                "nlpToken": {
                  "index": 24,
                  "word": "6am",
                  "originalText": "6am",
                  "lemma": "6am",
                  "characterOffsetBegin": 316,
                  "characterOffsetEnd": 319,
                  "pos": "JJ",
                  "ner": "TIME",
                  "normalizedNER": "T06:00",
                  "speaker": "PER0",
                  "before": " ",
                  "after": "",
                  "timex": {
                    "tid": "t1",
                    "type": "TIME",
                    "value": "T06:00"
                  }
                },
                "heideltime": [
                  {
                    "@tid": "t1",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "@mod": "APPROX",
                    "#text": "around 6am.",
                    "characterOffset": [
                      309,
                      320
                    ]
                  },
                  {
                    "@tid": "t2",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "@mod": "APPROX",
                    "#text": "around 6am.",
                    "characterOffset": [
                      309,
                      320
                    ]
                  },
                  {
                    "@tid": "t3",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "#text": "6am",
                    "characterOffset": [
                      316,
                      319
                    ]
                  }
                ]
              },
              "JJ"
            ],
            [
              {
                "nlpToken": {
                  "index": 25,
                  "word": ".",
                  "originalText": ".",
                  "lemma": ".",
                  "characterOffsetBegin": 319,
                  "characterOffsetEnd": 320,
                  "pos": ".",
                  "ner": "TIME",
                  "normalizedNER": "T06:00",
                  "speaker": "PER0",
                  "before": "",
                  "after": " ",
                  "timex": {
                    "tid": "t1",
                    "type": "TIME",
                    "value": "T06:00"
                  }
                },
                "heideltime": [
                  {
                    "@tid": "t1",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "@mod": "APPROX",
                    "#text": "around 6am.",
                    "characterOffset": [
                      309,
                      320
                    ]
                  },
                  {
                    "@tid": "t2",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "@mod": "APPROX",
                    "#text": "around 6am.",
                    "characterOffset": [
                      309,
                      320
                    ]
                  },
                  {
                    "@tid": "t3",
                    "@type": "TIME",
                    "@value": "XXXX-XX-XXT06:00",
                    "#text": "6am",
                    "characterOffset": [
                      316,
                      319
                    ]
                  }
                ]
              },
              "."
            ]
          ],
          "score": 0.8543371522094926,
          "text": "6am .",
          "nlpIndexSentence": 2
        }
      ]
    }
```

# Startup - Scripts -> Giveme5W-runtime-resources
Giveme5W can start up everything. Check examples/startup scripts.
To do so, all libraries must be located in the same directory 'runtime-resources' located inside Giveme5W .

- Folder Structure
    - Giveme5W                      (Master)
        - runtime-resources
            - aida-3.0.4
            - heideltime-standalone
            - stanford-corenlp-full-2016-10-31
            - treeTagger
    - Giveme5W_NewsCluster_enhancer (Master)

You can change this directory with:
```shell
Config.get()['Giveme5W-runtime-resources'] = './runtime-resources'
```

# License
The project is licensed under the Apache License 2.0. Make sure that you use Giveme5W in compliance with applicable law. Copyright 2016 The Giveme5W team
