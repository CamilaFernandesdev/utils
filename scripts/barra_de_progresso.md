```py
from tqdm import tqdm
```

```py
# Barra de progresso
with tqdm(total=len(arquivos) * len(postos_corr)) as pbar:
    """Execução"""
    def executa_alguma_coisa():
      """Exemplo, pode ser um loop, etc"""
      pass
    executa_alguma_coisa()
    # Atualiza barra de progresso
    pbar.update(1)  
```

```py
# Quantidade de anos em uma chave
# Itera sobre os valores do dicionário
length_values_anos_definidos = len(next(iter(dicionario_anos_definidos.values())))
```
