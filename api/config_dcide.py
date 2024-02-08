def cfg_dcide_api() -> dict[str, str]:
    """
    Dados de conexão com a API da DCIDE.

    Returns
    -------
    dict[str, str]

    """
    # Leitura do arquivo (novamente para garantir novas mudanças)
    CONFIG.read(CONFIG_FILE)
    try:
        # Tenta pegar os dados do arquivo de configuração
        cfg = CONFIG['dcide_api']
    except KeyError:
        # Tenta pegar os dados do Airflow
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection('dcide_api')
        return {'userName': conn.login,
                'senha': conn.password,
                'verify_ssl': True,
                }
    else:
        # Retorna os dados lidos do arquivo de configuração
        return {'userName': cfg['login'],
                'senha': cfg.get('password', raw=True),
                'verify_ssl': False,
                }
