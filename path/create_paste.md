
```py
from  pathlib import Path
```



```py
caminho = 'caminho do arquivo'
pasta_entrada = Path(caminho)
```



```py
pasta_saida = pasta_entrada / 'nome_da_pasta'

    try:
        # Criação da pasta de saída
        pasta_saida.mkdir()
    except FileExistsError:
        # Limpeza da pasta de saída se ela já existia
        # Todos os arquivos de texto
        for arquivo in pasta_saida.glob('*.txt'):
            if arquivo.is_file():
                arquivo.unlink()
```

