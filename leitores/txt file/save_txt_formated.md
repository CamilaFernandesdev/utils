```py
from typing import Optional, Union
```

```py
def salvar_txt(self,
                   arquivo_destino: Union[str, Path],
                   ) -> None:
        """
        Salva o dataframe modificado em um novo arquivo de vazões.txt.

        Parameters
        ----------
        arquivo_destino : str or Path
            Nome ou caminho do arquivo de destino.

        """
        lista_linhas = list()
        for idx, row in self.df_arquivo.iterrows():
            lista_linhas.append(f"{idx[0]:3} {idx[1]:4}"
                                f"{row[1]:6}{row[2]:6}{row[3]:6}"
                                f"{row[4]:6}{row[5]:6}{row[6]:6}"
                                f"{row[7]:6}{row[8]:6}{row[9]:6}"
                                f"{row[10]:6}{row[11]:6}{row[12]:6}")

        conteudo_arquivo = '\n'.join(lista_linhas)

        with open(arquivo_destino, 'w') as file:
            file.write(conteudo_arquivo)
            file.write('\n')
            
```
