 # Quantidade de anos em uma chave
    # Itera sobre os valores do dicionário
    length_values_anos_definidos = len(next(iter(anos_definidos.values())))


pasta_saida = pasta_entrada / 'saida_vaz20'

    try:
        # Criação da pasta de saída
        pasta_saida.mkdir()
    except FileExistsError:
        # Limpeza da pasta de saída se ela já existia
        for arquivo in pasta_saida.glob('*.txt'):
            if arquivo.is_file():
                arquivo.unlink()


# Parametrização do modelo
                        try:
                            model.fit(vazoes.df_period)
                        except Exception:
                            print(f'Não foi possível o fit para {arquivo.stem}'
                                  f'-{anos}')
                            continue
