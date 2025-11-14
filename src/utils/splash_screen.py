from conexion.oracle_queries import OracleQueries
from utils import config

class SplashScreen:

    def __init__(self):
        # Consultas de contagem de registros - início (com schema + alias corretos)
        self.qry_total_marcacoes = config.QUERY_COUNT.format(
            alias="total_marcacoes", table="MARCACOES"
        )
        self.qry_total_funcionarios = config.QUERY_COUNT.format(
            alias="total_funcionarios", table="FUNCIONARIOS"
        )
        # Consultas de contagem de registros - fim

        self.created_by = "Hellen Karla Costa Campos de Melo, Julia Ogassavara Maia e Yasmim Luiz dos Santos"
        self.professor  = "Prof. M.Sc. Howard Roatti"
        self.disciplina = "Banco de Dados"
        self.semestre   = "2025/2"

    def get_total_marcacoes(self):
        # Cria uma nova conexão com o banco
        oracle = OracleQueries()
        oracle.connect()
        # Retorna o total de registros
        return oracle.sqlToDataFrame(self.qry_total_marcacoes)["total_marcacoes"].values[0]

    def get_total_funcionarios(self):
        # Cria uma nova conexão com o banco
        oracle = OracleQueries()
        oracle.connect()
        # Retorna o total de registros
        return oracle.sqlToDataFrame(self.qry_total_funcionarios)["total_funcionarios"].values[0]

    def get_updated_screen(self):
        return f"""
        ########################################################
        #        SISTEMA DE CONTROLE DE MARCAÇÕES DE PONTO      
        #                                                      
        #  TOTAL DE REGISTROS:                                 
        #      1 - MARCAÇÕES:   {str(self.get_total_marcacoes()).rjust(5)}
        #      2 - FUNCIONÁRIOS:{str(self.get_total_funcionarios()).rjust(5)}
        #
        #  CRIADO POR: {self.created_by}
        #
        #  PROFESSOR:  {self.professor}
        #
        #  DISCIPLINA: {self.disciplina}
        #              {self.semestre}
        ########################################################
        """
