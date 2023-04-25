import re
import tempfile
from pathlib import Path


def get_file_temp_folder(re_name: str) -> str:
    """Localiza um arquivo com nome que corresponde a um padrão de expressão regular na pasta temporária.

    Parâmetros
    ----------
    re_name : str
        O padrão de expressão regular que será usado para encontrar o arquivo.

    Retorna
    -------
    filepath: str
        O caminho completo para o arquivo encontrado, ou None se nenhum arquivo
        corresponder ao padrão.
    """
    temp_dir = Path(tempfile.gettempdir())
    file_name_pattern = re.compile(r'(?i)^Detalhamento *- *Dados.csv$')
    filepath = next((temp_file for temp_file in temp_dir.glob('*') if file_name_pattern.match(temp_file.name)), None)
    return filepath

