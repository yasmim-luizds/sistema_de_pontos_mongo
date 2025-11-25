import pandas as pd

from model.funcionario import Funcionario
from conexion.mongo_queries import MongoQueries


def _esc(s: str) -> str:
    return str(s).replace("'", "''")


class Controller_Funcionario:
    def __init__(self):
        self.mongo = MongoQueries()
    def inserir_funcionario(self) -> Funcionario | None:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        nome  = _esc(input("Nome: ").strip())
        cpf   = _esc(input("CPF (somente números): ").strip())
        cargo = _esc(input("Cargo: ").strip())

        # Verifica se já existe funcionário com esse CPF
        if self.verifica_existencia_cpf(cpf):
            # Busca o MAIOR id_func já existente e soma 1
            ultimo = self.mongo.db["funcionarios"].find_one(
                {},                      # qualquer documento
                sort=[("id_func", -1)]   # ordena por id_func desc
            )

            if ultimo is None:
                proximo_id = 1
            else:
                proximo_id = int(ultimo.get("id_func", 0)) + 1

            # Monta o documento para inserir
            data = dict(
                id_func=proximo_id,
                nome=nome,
                cpf=cpf,
                cargo=cargo
            )

            # Insere o documento no MongoDB
            self.mongo.db["funcionarios"].insert_one(data)

            # Recupera o funcionário recém inserido em forma de DataFrame
            df_func = self.recupera_funcionario(proximo_id)

            # Cria o objeto Funcionario
            novo = Funcionario(
                df_func.id_func.values[0],
                df_func.nome.values[0],
                df_func.cpf.values[0],
                df_func.cargo.values[0]
            )

            print("Funcionário inserido com sucesso!")
            print(novo.to_string())

            self.mongo.close()
            return novo
        else:
            print(f"O CPF {cpf} já está cadastrado.")
            self.mongo.close()
            return None

    def atualizar_funcionario(self) -> Funcionario | None:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        try:
            id_func = int(input("ID do Funcionário que irá alterar: ").strip())
        except ValueError:
            print("ID inválido.")
            self.mongo.close()
            return None

        # Verifica se o funcionário existe (False = existe, True = não existe)
        if not self.verifica_existencia_funcionario(id_func):
            novo_nome  = _esc(input("Nome (Novo): ").strip())
            novo_cargo = _esc(input("Cargo (Novo): ").strip())

            # Atualiza no MongoDB
            self.mongo.db["funcionarios"].update_one(
                {"id_func": id_func},
                {"$set": {"nome": novo_nome, "cargo": novo_cargo}}
            )

            # Recupera dados atualizados
            df_func = self.recupera_funcionario(id_func)
            atualizado = Funcionario(
                df_func.id_func.values[0],
                df_func.nome.values[0],
                df_func.cpf.values[0],
                df_func.cargo.values[0]
            )

            print("Funcionário atualizado com sucesso!")
            print(atualizado.to_string())

            self.mongo.close()
            return atualizado
        else:
            print(f"O id_func {id_func} não existe.")
            self.mongo.close()
            return None

    def excluir_funcionario(self) -> None:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        try:
            id_func = int(input("ID do Funcionário que irá excluir: ").strip())
        except ValueError:
            print("ID inválido.")
            self.mongo.close()
            return

        # Verifica se o funcionário existe
        if not self.verifica_existencia_funcionario(id_func):
            # Recupera dados antes de excluir
            df_func = self.recupera_funcionario(id_func)

            # Remove o funcionário da coleção
            self.mongo.db["funcionarios"].delete_one({"id_func": id_func})

            excluido = Funcionario(
                df_func.id_func.values[0],
                df_func.nome.values[0],
                df_func.cpf.values[0],
                df_func.cargo.values[0]
            )

            print("Funcionário removido com sucesso!")
            print(excluido.to_string())
            self.mongo.close()
        else:
            print(f"O id_func {id_func} não existe.")
            self.mongo.close()

    def verifica_existencia_funcionario(self, id_func: int = None, external: bool = False) -> bool:
        if external:
            self.mongo.connect()

        df_func = pd.DataFrame(
            self.mongo.db["funcionarios"].find(
                {"id_func": id_func},
                {"id_func": 1, "nome": 1, "cpf": 1, "cargo": 1, "_id": 0}
            )
        )

        if external:
            self.mongo.close()

        return df_func.empty

    def verifica_existencia_cpf(self, cpf: str = None, external: bool = False) -> bool:
        if external:
            self.mongo.connect()

        df_func = pd.DataFrame(
            self.mongo.db["funcionarios"].find(
                {"cpf": cpf},
                {"id_func": 1, "nome": 1, "cpf": 1, "cargo": 1, "_id": 0} 
            )
        )

        if external:
            self.mongo.close()

        return df_func.empty

    def recupera_funcionario(self, id_func: int = None, external: bool = False) -> pd.DataFrame:
        if external:
            self.mongo.connect()

        df_func = pd.DataFrame(
            list(
                self.mongo.db["funcionarios"].find(
                    {"id_func": id_func},
                    {"id_func": 1, "nome": 1, "cpf": 1, "cargo": 1, "_id": 0}
                )
            )
        )

        if external:
            self.mongo.close()

        return df_func
