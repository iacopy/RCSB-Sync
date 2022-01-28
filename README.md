RCSB-Sync
=========

Automatizza il download di strutture proteiche dal server remoto RCSB.

Supporta il resume, cioè si può interrompere il download, e al successivo lancio il download riprenderà dal punto a cui era arrivato.

Esempio:

    python src/organism.py ~/your_project/Rattus_norvegicus/ -j 2

Funzionamento
-------------

Il programma è pensato per sincronizzare la directory di lavoro col database remoto.
Se il programma viene lanciato in giorni diversi, la prima volta di ogni giorno effettuerà nuovamente la ricerca su www.rcsb.org
per ottenere la lista degli IDs eventualmente aggiornata.

Se la directory locale non è sincronizzata, viene chiesto all'utente se effettuare la sincronizzazione
(scaricare i file non ancora presenti in locale e/o marcare i file obsoleti).
Se un file già scaricato non è più presente nella lista degli IDs scaricata, questo verrà marcato come obsoleto,
tramite l'aggiunta di un suffisso al nome del file.

Vengono scaricati file .pdb in formato compresso (.gz).

Struttura directory
-------------------

Lo script è pensato per lavorare su directory organizzate in questo modo:

    .
    ├── Rattus_norvegicus  # creato manualmente
    │   ├── _ids_2022-01-01.txt  # creato automaticamente
    │   ├── _ids_2022-03-01.txt  # creato automaticamente
    │   ├── queries    # creata manualmente
    │   │   ├── query_0.json  # creata manualmente, nome arbitrario, necessaria almeno una
    │   │   ├── query_1.json  # come sopra
    │   │   └── query_2.json  # come sopra
    │   └── data  # creata automaticamente
    │       ├── 1i5r.pdb.gz  # scaricato automaticamente
    │       ├── 1k8o.pdb.gz  # come sopra
    │       .
    │       .
    │       .
    │       └── 1q9s.pdb.gz  # come sopra

Preparazione query
------------------

La sottodirectory `queries` deve essere popolata manualmente, la prima volta.
Serve almeno una query in formato JSON per ottenere automaticamente la lista dei PDB IDs che saranno utilizzati per scaricare i file .pdb delle strutture proteiche.

Per generare la query JSON basta fare una volta la ricerca desiderata online su <https://www.rcsb.org/search/advanced> utilizzando il browser.
Una volta definiti i campi di interesse, effettuare la ricerca premendo la lente. Apparirà in alto la stringa della query di ricerca con a destra il tasto JSON.
Premere il tasto, si aprirà una nuova tab con la stringa JSON.
Non eseguire la query, ma effettuare la copia della stringa JSON a sinistra (si può fare manualmente se si vuole mantenere la formattazione con l'indentazione,
altrimenti il tasto copia la comprime in una sola riga).

Creare un file .json che contenga tale stringa e posizionarlo dentro la cartella `queries`.

Attenzione: modificare il valore `rows` che di default è 25, e impostarlo ad un valore superiore al numero totale di strutture restituite da quell'organismo.
Per esempio, per l'uomo si può mettere anche 99999, in questo modo scarica tutti gli ID delle 55k strutture in un colpo solo,
senza bisogno di fare 3 query con 3 range di data. Non so quale sia il valore massimo accettato, ma per ora funziona.
