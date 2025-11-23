from conexion.mongo_queries import MongoQueries
import pandas as pd
from pymongo import ASCENDING


class Relatorio:
    def __init__(self):
        pass

    def get_relatorio_funcionarios(self):
        mongo = MongoQueries()
        mongo.connect()

        query_result = mongo.db["funcionarios"].find(
            {},
            {
                "id_func": 1,
                "nome": 1,
                "cpf": 1,
                "cargo": 1,
                "_id": 0
            }
        ).sort("nome", ASCENDING)

        df = pd.DataFrame(list(query_result))

        mongo.close()

        if df.empty:
            print("Nenhum funcionário cadastrado.")
        else:
            print(df)

        input("Pressione Enter para Sair do Relatório de Funcionários")

    def get_relatorio_marcacao(self):
        mongo = MongoQueries()
        mongo.connect()

        pipeline = [
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "id_func",
                    "foreignField": "id_func",
                    "as": "funcionario"
                }
            },
            {
                "$unwind": {
                    "path": "$funcionario",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "id_marc": 1,
                    "data_marc": 1,
                    "hora_entrada": 1,
                    "hora_saida": 1,
                    "tipo": 1,
                    "id_func": 1,
                    "nome": "$funcionario.nome",
                    "cpf": "$funcionario.cpf",
                    "cargo": "$funcionario.cargo",
                    "_id": 0
                }
            },
            {
                "$sort": {
                    "data_marc": 1,
                    "id_marc": 1
                }
            }
        ]

        query_result = mongo.db["marcacoes"].aggregate(pipeline)
        df = pd.DataFrame(list(query_result))

        mongo.close()

        if df.empty:
            print("Nenhuma marcação registrada.")
        else:
            print(df)

        input("Pressione Enter para Sair do Relatório de Marcações de Ponto")

    def get_relatorio_pontos_funcionarios(self):
        mongo = MongoQueries()
        mongo.connect()

        pipeline = [
            {
                "$group": {
                    "_id": "$id_func",
                    "qtd_marcacoes": {"$sum": 1}
                }
            },
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "_id",
                    "foreignField": "id_func",
                    "as": "funcionario"
                }
            },
            {
                "$unwind": {
                    "path": "$funcionario",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "id_func": "$_id",
                    "nome": "$funcionario.nome",
                    "cpf": "$funcionario.cpf",
                    "cargo": "$funcionario.cargo",
                    "qtd_marcacoes": 1,
                    "_id": 0
                }
            },
            {
                "$sort": {
                    "nome": 1
                }
            }
        ]

        query_result = mongo.db["marcacoes"].aggregate(pipeline)
        df = pd.DataFrame(list(query_result))

        mongo.close()

        if df.empty:
            print("Nenhuma marcação registrada.")
        else:
            print(df)

        input("Pressione Enter para Sair do Relatório de Marcações por Funcionário")
