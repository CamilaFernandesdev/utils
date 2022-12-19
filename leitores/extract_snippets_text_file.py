# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 15:14:48 2022
@author: Rodrigo Fagundes Eggea
"""

import re
from io import StringIO
import warnings
import pandas as pd
warnings.filterwarnings("ignore")

def extraiTabela(conteudo : str, regex_inicio : str, regex_fim : str, skip_rows = 0, skip_footer = 0):
    """
    Busca em uma String uma tabela com texto de inicio e fim em expressão regular
    Arguments:
        str: string
        regex_inicio: string
        regex_fim : string
    Returns:
        String contendo apenas a tabela procurada
    """
    lines=conteudo.splitlines(True)   # MANTEM O NEWLINE
    # BUSCA O ITERATOR
    iter=lines.__iter__()

    # PROCURA O INICIO DA TABELA
    end_cursor = False
    index = 0
    inicio = 0
    while not end_cursor:
        index += 1
        try:        
            line = iter.__next__()
            if re.search(regex_inicio, line) != None:
                inicio = index
                break
        except StopIteration:
            end_cursor = True

    if inicio == 0:
       raise Exception("ERRO: INICIO DA TABELA NAO ENCONTRADO")

    # PROCURA O FIM DA TABELA
    end_cursor = False
    fim=0
    while not end_cursor:
        index+=1
        try:
            line=iter.__next__()
            if re.search(regex_fim, line) != None:
                fim = index
                break
        except StopIteration:
            end_cursor = True
        
    if fim == 0:
        raise Exception("ERRO: FIM DA TABELA NAO ENCONTRADO")

    # CRIA UMA SUBLISTA 
    sublista = lines[inicio + skip_rows : fim - skip_footer]

    # CONVERTE LISTA EM STRING 
    tabela_str =''.join(sublista)
    return tabela_str

####################################################################################
f = open("drive/My Drive/parp.dat", "r")
conteudo = f.read()

### BUSCA TABELA REE:SUL NO ARQUIVO ###
# ATENÇÃO: PARANTESES EM REGEXP É UM CARACTERE ESPECIAL!!! TEM QUE COLOCA \( \)

regex_inicio = ".*SERIE  DE ENERGIAS DO REE   SUDESTE      \(CONFIGURACAO No.    1\).*"  
regex_fim    = ".*MEDIA AMOSTRAL DAS ENERGIAS.*"    # LINHA SEM NADA
tabela_str = extraiTabela(conteudo, regex_inicio, regex_fim, 3, 3)
#print(tabela_str)

### TRATA OS DADOS ANTES DE CARREGAR NO PANDAS ###
csvStringIO = StringIO(tabela_str)
columns=['ano','jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov']
df = pd.read_csv(csvStringIO, header=None, sep=r"\s+", skiprows=0, skipfooter=0, names=columns, index_col=False)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', None)
print(df)
#print(df[df["ano"] == 2020])
#print(df[df["fev"] == 1874.9])
#my_float = df[df["ano"] == 2020]["abr"].values[0]
#print("2020 ABR => " + str(my_float))
#print("2020 ABR => ",my_float)
