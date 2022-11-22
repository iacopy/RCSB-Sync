"""
Parse PDB file content.
"""

# pylint: disable=trailing-whitespace
TESTDATA = """HEADER    TRANSFERASE                             11-AUG-05   2AN4              
TITLE     STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE    
TITLE    2 ACCEPTOR SUBSTRATE OCTOPAMINE                                        
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: PHENYLETHANOLAMINE N-METHYLTRANSFERASE;                    
COMPND   3 CHAIN: A, B;                                                         
COMPND   4 SYNONYM: PNMTASE, NORADRENALINE N-METHYLTRANSFERASE;                 
COMPND   5 EC: 2.1.1.28;                                                        
"""  # noqa


def parse_title(pdb_lines_iterable):
    """
    Read the title from a PDB iterator content.

    >>> parse_title(TESTDATA.splitlines())
    'STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE ACCEPTOR SUBSTRATE OCTOPAMINE'
    >>> parse_title([])
    ''
    """
    title = []
    for line in pdb_lines_iterable:
        if line.startswith("TITLE"):
            title.append(line[10:].rstrip())
        elif title:
            break
    return "".join(title)


if __name__ == "__main__":
    # Standard Library
    import doctest

    doctest.testmod()
