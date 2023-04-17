
# Variáveis Nulas 
## Criando Expections

DICIONÁRIO

```python
# Check if the dictionary contains informations
dicionario = dict()
if bool(dicionario) == False:
    raise ValueError("O dicionário está vazio, não foi criado corretamente")
```


LISTAS
```python
# Check if the list is empty
lista = list()
if not lista:
    raise ValueError("A lista está vazia")
```
