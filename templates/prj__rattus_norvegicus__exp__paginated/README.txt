Progetto RCSB-Sync per scaricare proteine sperimentali di Rattus norvegicus.

Metodi sperimentali inclusi = X-RAY DIFFRACTION + SOLUTION NMR + ELECTRON MICROSCOPY

Al momento attuale, dato che le proteine sono meno di 4,000 (quindi meno di 10,000) è sufficiente una singola query.
In futuro, mano a mano che aumentano le proteine sperimentali depositate, basta creare una seconda query JSON per duplicazione,
sostituendo `"start": 0,` con `"start": 10000,`.

Lancio:

    $ python src/project.py templates/prj__rattus_norvegicus__exp__paginated -s
