
import logging
import json

import pandas as pd

from conexion.mongo_queries import MongoQueries
from conexion.oracle_queries import OracleQueries

LIST_OF_COLLECTIONS = ["funcionarios", "marcacoes"] # listas de coleções a serem criadas

logger = logging.getLogger(name="SistemaPonto_Mongo_Migration")
logger.setLevel(level=logging.WARNING)

mongo = MongoQueries()


def createCollections(drop_if_exists: bool = False):
    mongo.connect()
    existing_collections = mongo.db.list_collection_names()

    for collection in LIST_OF_COLLECTIONS:
        if collection in existing_collections: 
            if drop_if_exists:
                mongo.db.drop_collection(collection)
                logger.warning(f"{collection} droped!") # se existir, apaga
                mongo.db.create_collection(collection)
                logger.warning(f"{collection} created!") # cria nova coleção
        else:
            mongo.db.create_collection(collection)
            logger.warning(f"{collection} created!") 

    mongo.close()


def insert_many(data: list[dict], collection: str):
    mongo.connect()
    mongo.db[collection].insert_many(data)
    mongo.close()


def extract_and_insert():
    oracle = OracleQueries()
    oracle.connect()

    for collection in LIST_OF_COLLECTIONS:
        sql = f"SELECT * FROM labdatabase.{collection}"
        df = oracle.sqlToDataFrame(sql)

        logger.warning(f"Data extracted from Oracle labdatabase.{collection}")

        if collection == "funcionarios":
            mapping = {
                "CODIGO_FUNCIONARIO": "id_func",
                "NOME": "nome",
                "CPF": "cpf",
                "CARGO": "cargo",
            }
            # Renomeia colunas para o padrão Mongo
            df.rename(columns=mapping, inplace=True)

        elif collection == "marcacoes":
  
            mapping = {
                "CODIGO_MARCACAO": "id_marc",
                "CODIGO_FUNCIONARIO": "id_func",
                "DATA_MARCACAO": "data_marc",
                "HORA_ENTRADA": "hora_entrada",
                "HORA_SAIDA": "hora_saida",
                "TIPO": "tipo",
            }
            df.rename(columns=mapping, inplace=True)

            # Converte datas/horas para string (caso venham como datetime/time)
            if "data_marc" in df.columns:
                try:
                    df["data_marc"] = df["data_marc"].dt.strftime("%d-%m-%Y")
                except Exception:
                    df["data_marc"] = df["data_marc"].astype(str)

            for col in ["hora_entrada", "hora_saida"]:
                if col in df.columns:
                    try:
                        df[col] = df[col].dt.strftime("%H:%M")
                    except Exception:
                        df[col] = df[col].astype(str)

        # Mantém apenas colunas minúsculas (padrão Mongo)
        df = df[[c for c in df.columns if c.islower()]]

       # Converte DataFrame para lista de dicionários (JSON)
        records = json.loads(df.T.to_json()).values()

        logger.warning("Data converted to json")
        insert_many(data=list(records), collection=collection)
        logger.warning(f"Documents generated at '{collection}' collection")


if __name__ == "__main__":
    logging.warning("Starting migration for Sistema de Ponto")
    createCollections(drop_if_exists=True)
    extract_and_insert()
    logging.warning("End migration")
