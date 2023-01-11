# Classe Utils
# Organizar posteriomente os módulos
class TabelaUtils:
    @staticmethod
    def extraiTabela(conteudo : str, regex_inicio : str, regex_fim : str, n_footer = 0, skip_rows = 0, skip_footer = 0):
        """
        Busca em uma String uma tabela com texto de inicio e fim em expressão regular
        Arguments:
            str: string
            regex_inicio: string para match do cabeçalho
            regex_fim : string para match do rodapé
            n_footer  : número de vezes que o rodapé tem que repetir (0 => para no primeiro match, 1 => match no segundo match, ...)
            skip_rows: número de linhas para pular do inicio
            skip_footer: número de linhas retorna no final
        Returns:
            String contendo apenas a tabela procurada
        """
        lines=conteudo.splitlines(True)   # MANTEM O NEWLINE
        # BUSCA O ITERATOR
        iter=lines.__iter__()

        # PROCURA O INICIO DA TABELA
        end_cursor = False
        index = 0
        inicio = 0
        while not end_cursor:
            index += 1
            try:        
                line = iter.__next__()
                if re.search(regex_inicio, line) != None:
                    inicio = index
                    break
            except StopIteration:
                end_cursor = True

        if inicio == 0:
            raise Exception("ERRO: INICIO DA TABELA NAO ENCONTRADO")

        # PROCURA O FIM DA TABELA
        end_cursor = False
        fim=0
        match=0

        while n_footer >= 0:
            while not end_cursor:
                index+=1
                try:
                    line=iter.__next__()
                    if re.search(regex_fim, line) != None:
                        fim = index
                        n_footer-=1
                        break
                except StopIteration:
                    end_cursor = True
                
        if fim == 0 :
            raise Exception("ERRO: FIM DA TABELA NAO ENCONTRADO")

        # CRIA UMA SUBLISTA 
        sublista = lines[inicio + skip_rows : fim - skip_footer]

        # CONVERTE LISTA EM STRING 
        tabela_str =''.join(sublista)
        return tabela_str
