# RCSB-Sync

[![Testing](https://github.com/iacopy/RCSB-Sync/actions/workflows/ci.yml/badge.svg)](https://github.com/iacopy/RCSB-Sync/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/iacopy/RCSB-Sync/branch/main/graph/badge.svg?token=WR8dFNq0ci)](https://codecov.io/gh/iacopy/RCSB-Sync)
[![Coverage badge](https://raw.githubusercontent.com/iacopy/RCSB-Sync/python-coverage-comment-action-data/badge.svg)](https://github.com/iacopy/RCSB-Sync/tree/python-coverage-comment-action-data)
[![Maintainability](https://api.codeclimate.com/v1/badges/0949c1768e6a83ea9a35/maintainability)](https://codeclimate.com/github/iacopy/RCSB-Sync/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automatizza il download di strutture proteiche dal server remoto RCSB.

Esempio:

    python src/project.py ~/your_project/Rattus_norvegicus/ -j 2

Vedi la documentazione su https://iacopy.github.io/rcsb-sync/.

## Funzionamento

Il programma sincronizza la directory di lavoro col database remoto.

Supporta il resume, cioè si può interrompere il download, e al successivo lancio il download riprenderà dal punto a cui era arrivato.

Quando il programma viene lanciato effetta una ricerca su www.rcsb.org, utilizzando le query impostate,
per ottenere la lista dei PDB IDs aggiornata.

Se la directory locale non è sincronizzata, viene chiesto all'utente se effettuare la sincronizzazione
(scaricare i file non ancora presenti in locale e/o marcare i file obsoleti).
Se un file già scaricato non è più presente nella lista degli IDs scaricata, questo verrà marcato come obsoleto,
tramite l'aggiunta di un suffisso al nome del file.

Vengono scaricati file .pdb in formato compresso (.gz).

## Struttura directory

Lo script è pensato per lavorare su directory organizzate in questo modo:

    .
    ├── Project_name   # creato manualmente
    │   ├── queries    # creata manualmente
    │   │   ├── query_x.json  # creata manualmente, nome arbitrario, necessaria almeno una
    │   │   └── query_y.json  # come sopra
    │   │
    │   └── data  # creata automaticamente
    │       ├── query_x
    │       │   ├── 1abc.pdb  # scaricato automaticamente
    │       │   ├── 7kik.pdb  # scaricato automaticamente
    │       │   └── 3e6x.pdb  # scaricato automaticamente
    │       └── query_y
    |           ├── 2i5r.pdb.gz  # scaricato automaticamente
    │           ├── 1k8o.pdb.gz  # scaricato automaticamente
    │           .
    │           .
    │           .
    │           └── 5q9s.pdb.gz  # scaricato automaticamente

## Preparazione query

La sottodirectory `queries` deve essere popolata manualmente, la prima volta.
Serve almeno una query in formato JSON per ottenere automaticamente la lista dei PDB IDs che saranno utilizzati per scaricare i file .pdb delle strutture proteiche.

Per generare la query JSON basta fare una volta la ricerca desiderata online su <https://www.rcsb.org/search/advanced> utilizzando il browser.
Una volta definiti i campi di interesse, effettuare la ricerca premendo la lente. Apparirà in alto la stringa della query di ricerca con a destra il tasto JSON.
Premere il tasto, si aprirà una nuova tab con la stringa JSON.
Non eseguire la query, ma effettuare la copia della stringa JSON a sinistra (si può fare manualmente se si vuole mantenere la formattazione con l'indentazione,
altrimenti il tasto copia la comprime in una sola riga).

Creare un file .json che contenga tale stringa e posizionarlo dentro la cartella `queries`.

**Attenzione**: modificare il valore `rows` che di default è 25, e impostarlo ad un valore superiore al numero totale di strutture restituite da quella query.
Per esempio, per l'uomo si può mettere anche 999999, in questo modo scarica tutti gli ID delle 55k strutture in un colpo solo,
senza bisogno di fare 3 query con 3 range di data. Non so quale sia il valore massimo accettato, ma per ora funziona.

EDIT 2023: Dopo un aggiornamento (forse [2.4.11] - 2023-08-03), il valore massimo impostabile è 10000 (https://search.rcsb.org/#pagination).
Due opzioni:

    ```json
    "request_options": {
        "paginate": {
            "start": 0,
            "rows": 10000
        },
    ```

Poi:

    ```json
    "request_options": {
        "paginate": {
            "start": 10000,
            "rows": 10000
        },
    ```

E via di seguito.

Oppure:

    ```json
    "request_options": {
        "return_all_hits": true
    },
    ```

Quest'ultima è sconsigliata, ad es. se si vuole scaricare tutto in un blocco unico (Homo sapiens > 100 GB),
ma può essere utile in certi casi, ad esempio per ottenere tutti i PDB ID.

### Modulo `rcsbquery`

Per generare alcuni tipi di query, in formato JSON, si può utilizzare anche lo script `rcsbquery.py`.

Ottenere strutture proteiche sperimentali per l'uomo:

    python rcsbquery.py -p Protein -o "Homo sapiens" -m "X-RAY DIFFRACTION" "SOLUTION NMR" "ELECTRON MICROSCOPY"

Ottenere solo strutture dal DB AlphaFold per Volvox:

    python rcsbquery.py -o "Volvox" -m AlphaFoldDB --csm

Ottenere solo DNA:

    python rcsbquery.py -p "Nucleic acid (only)" DNA

## Esempi di query JSON

### Minimale (solo organism)

JSON:

    ```json
    {
        "query": {
            "type": "terminal",
            "label": "text",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
                "operator": "contains_phrase",
                "negation": false,
                "value": "Homo sapiens"
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 10000
            },
            "results_content_type": [
                "experimental"
            ],
            "sort": [
            {
                "sort_by": "score",
                "direction": "desc"
            }
            ],
            "scoring_strategy": "combined"
        }
    }
    ```

### Seleziona organismo e proteine

JSON:

    ```json
    {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
            {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "entity_poly.rcsb_entity_polymer_type",
                    "operator": "exact_match",
                    "negation": false,
                    "value": "Protein"
                }
            },
            {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
                    "operator": "contains_phrase",
                    "negation": false,
                    "value": "Homo sapiens"
                }
            }
            ],
            "label": "text"
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 25
            },
            "results_content_type": [
                "experimental"
            ],
            "sort": [
            {
                "sort_by": "score",
                "direction": "desc"
            }
            ],
            "scoring_strategy": "combined"
        }
    }
    ```

### Seleziona organismo, proteine e metodi specifici

JSON:

    ```json
    {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
            {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "entity_poly.rcsb_entity_polymer_type",
                    "operator": "exact_match",
                    "negation": false,
                    "value": "Protein"
                }
            },
            {
                "type": "group",
                "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "exptl.method",
                        "operator": "exact_match",
                        "negation": false,
                        "value": "X-RAY DIFFRACTION"
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "exptl.method",
                        "operator": "exact_match",
                        "negation": false,
                        "value": "SOLUTION NMR"
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "exptl.method",
                        "operator": "exact_match",
                        "negation": false,
                        "value": "ELECTRON MICROSCOPY"
                    }
                }
                ],
                "logical_operator": "or"
            },
            {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
                    "operator": "contains_phrase",
                    "negation": false,
                    "value": "Homo sapiens"
                }
            }
            ],
            "label": "text"
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 10000
            },
            "results_content_type": [
                "experimental"
            ],
            "sort": [
            {
                "sort_by": "score",
                "direction": "desc"
            }
            ],
            "scoring_strategy": "combined"
        }
    }
    ```
