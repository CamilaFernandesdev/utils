

def get_interval_index(data: pd.DataFrame,
                       filter_index,
                       intervalo_ini:int,
                       intervalo_end:int) -> list:
    """Seleciona um intervalo de index a partir de um determinado index.

    Args:
        data: pandas.DataFrame ou pandas.Series
        filter_index (_type_): valor selecionado
        intervalo_ini (int): quantidade de indexes antes do selecionado. Default=Null
        intervalo_ini (int): quantidade de indexes depois do selecionado.

    Returns
        list: lista com o intervalo apenas dos indexes
        
    """
    intervalo_ini = 0
    
    index_loc =data.index.get_loc(filter_index)
    ini_index = index_loc - intervalo_ini
    end_index = index_loc + intervalo_end
    indexes_selected = list(data.iloc[ini_index: end_index].index)
    
    return indexes_selected

  
  
