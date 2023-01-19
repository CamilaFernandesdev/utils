Importação das bibliotecas

```py
import argparse
from pathlib import Path

from module import classe, funçao
```


Para utilizar como linha de comando

```py
# Utiliza um parser para a entrada dos argumentos
parser = argparse.ArgumentParser(description='Adicione uma descrição topzeira aqui da funcao.')
parser.add_argument('pasta',
                    metavar='pasta',
                    type=str,
                    help='Pasta onde estao os arquivos')

args = parser.parse_args()
```

Execução do código
```py
# Roda o script
pasta_entrada = Path(args.pasta)
function_name(pasta_entrada)
```
