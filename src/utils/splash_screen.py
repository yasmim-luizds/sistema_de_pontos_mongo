from conexion.mongo_queries import MongoQueries


class SplashScreen:

    def __init__(self):
        self.created_by = "Hellen Karla Costa Campos de Melo, Julia Ogassavara Maia e Yasmim Luiz dos Santos"
        self.professor  = "Prof. M.Sc. Howard Roatti"
        self.disciplina = "Banco de Dados"
        self.semestre   = "2025/2"

    def get_total_marcacoes(self) -> int:
        # Cria uma nova conexão com o Mongo
        mongo = MongoQueries()
        mongo.connect()
        # Conta documentos na coleção de marcações
        total = mongo.db["marcacoes"].count_documents({})
        mongo.close()
        return total

    def get_total_funcionarios(self) -> int:
        # Cria uma nova conexão com o Mongo
        mongo = MongoQueries()
        mongo.connect()
        # Conta documentos na coleção de funcionários
        total = mongo.db["funcionarios"].count_documents({})
        mongo.close()
        return total

    def get_updated_screen(self) -> str:
        return f"""
        ########################################################
        #        SISTEMA DE CONTROLE DE MARCAÇÕES DE PONTO      
        #                 (MongoDB - labdatabase)               
        #                                                      
        #  TOTAL DE REGISTROS:                                 
        #      1 - MARCAÇÕES:    {str(self.get_total_marcacoes()).rjust(5)}
        #      2 - FUNCIONÁRIOS: {str(self.get_total_funcionarios()).rjust(5)}
        #
        #  CRIADO POR: {self.created_by}
        #
        #  PROFESSOR:  {self.professor}
        #
        #  DISCIPLINA: {self.disciplina}
        #              {self.semestre}
        ########################################################
        """
