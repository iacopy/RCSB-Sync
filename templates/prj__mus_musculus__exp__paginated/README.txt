Progetto RCSB-Sync per scaricare proteine sperimentali di Mus musculus.

Metodi sperimentali inclusi = X-RAY DIFFRACTION + SOLUTION NMR + ELECTRON MICROSCOPY

Al momento attuale, dato che le proteine sono poco meno di 9,000 (quindi meno di 10,000) è sufficiente una singola query.
In futuro, mano a mano che aumentano le proteine sperimentali depositate, basta creare una seconda query JSON per duplicazione,
sostituendo `"start": 0,` con `"start": 10000,`.

Lancio:

    $ python src/project.py templates/prj__mus_musculus__exp__paginated -s
