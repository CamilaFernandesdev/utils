def calc_corr_last12(df_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Cálculo da correlação dos últimos 12 meses informados com anos anteriores.

    Parameters
    ----------
    df_hist : DataFrame
        Dataframe do histórico a ser analisado.
        As 12 últimas linhas devem ser os 12 meses com os quais será calculada
        a correlação com dados de anos anteriores.

    Returns
    -------
    DataFrame
        Dataframe com as correlações calculadas.
        Como index é informado o mês final do período de 12 meses com o qual
        foi calculada a correlação.

    """
    # pylint: disable=protected-access
    # Conferindo se o index está no formato desejado (pd.PeriodIndex freq=M)
    if not isinstance(df_hist.index.freq, pd._libs.tslibs.offsets.MonthEnd):
        raise Exception("Favor informar dataframe periodizado mensalmente.")

    df_ref = df_hist.copy()
    # Trecho de 12 meses com o qual será calculada a correlação
    df_trecho = df_ref.iloc[-12:]
    # Espalha o trecho por uma cópia do dataframe respeitando os meses
    df_other = df_ref.copy()
    for month in range(1, 13):
        df_other[df_other.index.month == month] = df_trecho[df_trecho.index.month == month].iloc[0]

    # Calcula a correlação
    df_corr = df_ref.rolling(12).corr(df_other)
    # Filtra os dados da correlação com o mês final
    df_corr = df_corr[df_corr.index.month == df_trecho.index.month[-1]]
    df_corr.index.name = 'mes_final'

    return df_corr
