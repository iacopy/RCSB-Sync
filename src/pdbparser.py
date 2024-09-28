"""
Parse PDB file content.
"""

# Standard Library
import re
from typing import Dict
from typing import List
from typing import Union

# pylint: disable=trailing-whitespace
TESTDATA = """HEADER    TRANSFERASE                             11-AUG-05   2AN4              
TITLE     STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE    
TITLE    2 ACCEPTOR SUBSTRATE OCTOPAMINE                                        
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: PHENYLETHANOLAMINE N-METHYLTRANSFERASE;                    
COMPND   3 CHAIN: A, B;                                                         
COMPND   4 SYNONYM: PNMTASE, NORADRENALINE N-METHYLTRANSFERASE;                 
COMPND   5 EC: 2.1.1.28;                                                        
COMPND   6 ENGINEERED: YES                                                      
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;                                   
SOURCE   3 ORGANISM_COMMON: HUMAN;                                              
SOURCE   4 ORGANISM_TAXID: 9606;                                                
SOURCE   5 GENE: PNMT;                                                          
SOURCE   6 EXPRESSION_SYSTEM: ESCHERICHIA COLI;                                 
SOURCE   7 EXPRESSION_SYSTEM_TAXID: 562;                                        
SOURCE   8 EXPRESSION_SYSTEM_STRAIN: BL21(DE3)PLYSS;                            
SOURCE   9 EXPRESSION_SYSTEM_VECTOR_TYPE: PLASMID;                              
SOURCE  10 EXPRESSION_SYSTEM_PLASMID: PET17PNMT-HIS                             
KEYWDS    METHYLTRANSFERASE, SUBSTRATE STRUCTURE, S-ADENOSYL-L-METHIONINE,      
KEYWDS   2 ADRENALINE SYNTHESIS, TRANSFERASE                                    
EXPDTA    X-RAY DIFFRACTION                                                     
AUTHOR    C.L.GEE,J.D.A.TYNDALL,G.L.GRUNEWALD,Q.WU,M.J.MCLEISH,J.L.MARTIN       
REVDAT   3   13-JUL-11 2AN4    1       VERSN                                    
REVDAT   2   24-FEB-09 2AN4    1       VERSN                                    
REVDAT   1   14-MAR-06 2AN4    0                                                
JRNL        AUTH   C.L.GEE,J.D.A.TYNDALL,G.L.GRUNEWALD,Q.WU,M.J.MCLEISH,        
JRNL        AUTH 2 J.L.MARTIN                                                   
JRNL        TITL   MODE OF BINDING OF METHYL ACCEPTOR SUBSTRATES TO THE         
JRNL        TITL 2 ADRENALINE-SYNTHESIZING ENZYME PHENYLETHANOLAMINE            
JRNL        TITL 3 N-METHYLTRANSFERASE: IMPLICATIONS FOR CATALYSIS              
JRNL        REF    BIOCHEMISTRY                  V.  44 16875 2005              
JRNL        REFN                   ISSN 0006-2960                               
JRNL        PMID   16363801                                                     
JRNL        DOI    10.1021/BI051636B                                            
REMARK   2                                                                      
REMARK   2 RESOLUTION.    2.20 ANGSTROMS.                                       
... qui sotto c'e' un'altra proteina (DNA-PK complessata con altre)
DBREF  7Z87 A    1  4128  UNP    P78527   PRKDC_HUMAN      1   4128             
DBREF  7Z87 B    1   609  UNP    P12956   XRCC6_HUMAN      1    609             
DBREF  7Z87 C    1   732  UNP    P13010   XRCC5_HUMAN      1    732             
DBREF  7Z87 D    1    26  PDB    7Z87     7Z87             1     26             
DBREF  7Z87 E   18    43  PDB    7Z87     7Z87            18     43             
SEQRES   1 A 4128  MET ALA GLY SER GLY ALA GLY VAL ARG CYS SER LEU LEU          
"""  # noqa


TESTDATA_AF2 = """HEADER                                            01-JUN-22                     
TITLE     ALPHAFOLD MONOMER V2.0 PREDICTION FOR PIEZO DOMAIN-CONTAINING PROTEIN 
TITLE    2 (A0A3P7E792)                                                         
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: PIEZO DOMAIN-CONTAINING PROTEIN;                           
COMPND   3 CHAIN: A                                                             
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: WUCHERERIA BANCROFTI;                           
SOURCE   3 ORGANISM_TAXID: 6293                                                 
REMARK   1                                                                      
REMARK   1 REFERENCE 1                                                          
REMARK   1  AUTH   JOHN JUMPER, RICHARD EVANS, ALEXANDER PRITZEL, TIM GREEN,    
REMARK   1  AUTH 2 MICHAEL FIGURNOV, OLAF RONNEBERGER, KATHRYN TUNYASUVUNAKOOL, 
REMARK   1  AUTH 3 RUSS BATES, AUGUSTIN ZIDEK, ANNA POTAPENKO, ALEX BRIDGLAND,  
REMARK   1  AUTH 4 CLEMENS MEYER, SIMON A A KOHL, ANDREW J BALLARD,             
REMARK   1  AUTH 5 ANDREW COWIE, BERNARDINO ROMERA-PAREDES, STANISLAV NIKOLOV,  
REMARK   1  AUTH 6 RISHUB JAIN, JONAS ADLER, TREVOR BACK, STIG PETERSEN,        
REMARK   1  AUTH 7 DAVID REIMAN, ELLEN CLANCY, MICHAL ZIELINSKI,                
REMARK   1  AUTH 8 MARTIN STEINEGGER, MICHALINA PACHOLSKA, TAMAS BERGHAMMER,    
REMARK   1  AUTH 9 DAVID SILVER, ORIOL VINYALS, ANDREW W SENIOR,                
REMARK   1  AUTH10 KORAY KAVUKCUOGLU, PUSHMEET KOHLI, DEMIS HASSABIS            
REMARK   1  TITL   HIGHLY ACCURATE PROTEIN STRUCTURE PREDICTION WITH ALPHAFOLD  
REMARK   1  REF    NATURE                        V. 596   583 2021              
REMARK   1  REFN                   ISSN 0028-0836                               
REMARK   1  PMID   34265844                                                     
REMARK   1  DOI    10.1038/s41586-021-03819-2                                   
REMARK   1                                                                      
REMARK   1 DISCLAIMERS                                                          
REMARK   1 ALPHAFOLD DATA, COPYRIGHT (2021) DEEPMIND TECHNOLOGIES LIMITED. THE  
REMARK   1 INFORMATION PROVIDED IS THEORETICAL MODELLING ONLY AND CAUTION SHOULD
REMARK   1 BE EXERCISED IN ITS USE. IT IS PROVIDED "AS-IS" WITHOUT ANY WARRANTY 
REMARK   1 OF ANY KIND, WHETHER EXPRESSED OR IMPLIED. NO WARRANTY IS GIVEN THAT 
REMARK   1 USE OF THE INFORMATION SHALL NOT INFRINGE THE RIGHTS OF ANY THIRD    
REMARK   1 PARTY. THE INFORMATION IS NOT INTENDED TO BE A SUBSTITUTE FOR        
REMARK   1 PROFESSIONAL MEDICAL ADVICE, DIAGNOSIS, OR TREATMENT, AND DOES NOT   
REMARK   1 CONSTITUTE MEDICAL OR OTHER PROFESSIONAL ADVICE. IT IS AVAILABLE FOR 
REMARK   1 ACADEMIC AND COMMERCIAL PURPOSES, UNDER CC-BY 4.0 LICENCE.           
DBREF  XXXX A    1    82  UNP    A0A3P7E792 A0A3P7E792_WUCBA     1     82       
SEQRES   1 A   82  MET GLN LEU ARG ILE PHE ASN SER TRP TYR PHE GLN HIS          
SEQRES   2 A   82  CYS VAL VAL GLU TYR ARG SER ALA ALA VAL LEU MET ASN          
SEQRES   3 A   82  ARG GLY THR ILE LEU GLN ASP GLN LEU ILE GLU ARG GLU          
SEQRES   4 A   82  MET ILE GLU GLN LYS LYS GLN GLN GLU LYS LYS PHE LYS          
SEQRES   5 A   82  ASN ILE LYS MET ARG THR ASP GLN ILE ARG LYS ASP TYR          
SEQRES   6 A   82  GLU LYS ARG LEU SER LYS ALA GLY ALA PHE VAL PRO GLN          
SEQRES   7 A   82  THR TYR GLY GLN                                              
CRYST1    1.000    1.000    1.000  90.00  90.00  90.00 P 1           1          
ORIGX1      1.000000  0.000000  0.000000        0.00000                         
ORIGX2      0.000000  1.000000  0.000000        0.00000                         
ORIGX3      0.000000  0.000000  1.000000        0.00000                         
SCALE1      1.000000  0.000000  0.000000        0.00000                         
SCALE2      0.000000  1.000000  0.000000        0.00000                         
SCALE3      0.000000  0.000000  1.000000        0.00000                         
MODEL        1                                                              """  # noqa


HEADER_REGEPX = re.compile(r"HEADER\s{3,}(.+?)(\d{2}-\w{3}-\d{2})\s(.+)")

FIELDS = {
    "File name": "file_name",
    "Classification": "classification",
    "Date": "date",
    "PDB ID": "pdb_id",
    "Title": "title",
    "Source organism": "source_organism",
    "Method": "method",
    "Gene": "gene",
    "Uniprot": "uniprot",
}

MON_TO_NUM = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
}


def pdb_date_to_sortable(pdb_date: str) -> str:
    """
    Convert a PDB date to a sortable date.
    >>> pdb_date_to_sortable("11-AUG-05")
    '2005-08-11'
    >>> pdb_date_to_sortable("01-JUN-97")
    '1997-06-01'
    """
    day, month, year = pdb_date.split("-")
    year = f"20{year}" if year < "50" else f"19{year}"
    return f"{year}-{MON_TO_NUM[month]}-{day}"


def parse(pdb_lines_iterable, sortable_date=True) -> Dict[str, Union[str, List[str]]]:
    """
    Read the header from a PDB iterator content.

    >>> ret = parse(TESTDATA.splitlines(), sortable_date=False)
    >>> ret["classification"]
    'TRANSFERASE'
    >>> ret["date"]
    '11-AUG-05'
    >>> ret["pdb_id"]
    '2AN4'
    >>> ret["title"]
    'STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE ACCEPTOR SUBSTRATE OCTOPAMINE'
    >>> ret["source_organism"]
    ['HOMO SAPIENS']
    >>> ret["gene"]
    ['PNMT']
    >>> ret['method']
    ['X-RAY DIFFRACTION']
    >>> ret['uniprot']
    ['P78527', 'P12956', 'P13010']
    >>> ret = parse(TESTDATA_AF2.splitlines(), sortable_date=True)
    >>> ret["classification"]
    ''
    >>> ret["date"]
    '2022-06-01'
    >>> ret["pdb_id"]
    ''
    """
    ret: Dict[str, Union[str, List[str]]] = {}

    title = []
    source_organism = []
    method = []
    gene = []
    uniprot = []
    for line in pdb_lines_iterable:
        if line.startswith("HEADER"):
            findall = re.findall(HEADER_REGEPX, line)
            assert findall, line
            values = [val.strip() for val in re.findall(HEADER_REGEPX, line)[0]]
            if len(values) == 1:
                # It Should be the date of AlphaFold
                classification = ""
                date = values[0]
                pdb_id = ""
            else:
                assert len(values) == 3, values
                classification, date, pdb_id = values
            ret |= {
                "classification": classification,
                "date": pdb_date_to_sortable(date) if sortable_date else date,
                "pdb_id": pdb_id,
            }
        elif line.startswith("TITLE"):
            title.append(line[10:].strip())
        elif "SOURCE" in line and "ORGANISM_SCIENTIFIC" in line:
            source_organism.append(line[32:].rstrip().rstrip(";"))
        elif line[11:].startswith("GENE: "):
            gene.append(line[17:].strip().rstrip(";"))
        elif line.startswith("EXPDTA"):
            method.append(line[7:].strip())
        elif line.startswith("DBREF") and "UNP " in line:
            uniprot.append(line[32:42].strip())

    ret["gene"] = gene
    ret["source_organism"] = source_organism
    ret["uniprot"] = uniprot
    ret["method"] = method
    ret["title"] = " ".join(title)
    return ret


if __name__ == "__main__":
    # Standard Library
    import doctest

    doctest.testmod()
