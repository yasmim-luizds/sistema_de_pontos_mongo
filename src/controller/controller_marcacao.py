from model.marcacao import Marcacao
from conexion.mongo_queries import MongoQueries

def _esc(s: str) -> str:
    return str(s).replace("'", "''")
class Controller_Marcacao:
    def __init__(self):
        self.mongo = MongoQueries()

    def _resolve_funcionario(self, entrada: str) -> int | None:
        """
        Recebe um texto digitado pelo usuário.
        - Se for número, trata como ID e valida existência.
        - Se for nome, busca por nome (LIKE, case-insensitive).
          - 0 registros: avisa e retorna None
          - 1 registro: retorna o ID
          - >1 registros: lista opções e pede ID exato
        """
        entrada = entrada.strip()
        if entrada.isdigit():
            id_func = int(entrada)
            if self.verifica_existencia_funcionario(id_func):  # Verifica se o funcionário existe
                print(f"O ID do funcionário {id_func} não existe. Cadastre o funcionário primeiro.")
                return None
            return id_func

        nome = entrada.replace("'", "''")
        df = self.mongo.db["funcionarios"].find({"nome": {"$regex": nome, "$options": "i"}})

        funcionarios = list(df)

        if not funcionarios:
            print(f"Nenhum funcionário encontrado com nome contendo: {entrada}")
            return None
        if len(funcionarios) == 1:
            return funcionarios[0]['id_func']

        print("Foram encontrados vários funcionários:")
        for func in funcionarios:
            print(f"  {func['id_func']} - {func['nome']}")
        try:
            escolhido = int(input("Digite o ID exato do funcionário: ").strip())
        except ValueError:
            print("Entrada inválida.")
            return None

        if self.verifica_existencia_funcionario(escolhido):
            print(f"O ID {escolhido} não existe entre os resultados.")
            return None
        return escolhido

    def _get_open_period(self, id_func: int, data_marc: str):
        df = self.mongo.db["marcacoes"].find({
            "id_func": id_func,
            "data_marc": data_marc,
            "hora_entrada": {"$ne": None},
            "hora_saida": None
        }).sort("data_marc", -1).limit(1)

        marcacoes = list(df)
        if not marcacoes:
            return None
        return marcacoes[0]["id_marc"], marcacoes[0]["hora_entrada"]

    def inserir_marcacao(self) -> Marcacao | None:
        self.mongo.connect()

        entrada = input("Funcionário (ID ou Nome): ")
        id_func = self._resolve_funcionario(entrada)
        if id_func is None:
            return None

        tipo = input("Tipo (E=Entrada, S=Saída): ").strip().upper()[:1]
        if tipo not in {"E", "S"}:
            print("Tipo inválido. Use 'E' ou 'S'.")
            return None

        data_marc = input("Data (DD-MM-YYYY): ").strip()
        hora_marc = input("Hora (HH:MM): ").strip()

        if tipo == "E":
            aberto = self._get_open_period(id_func, data_marc)
            if aberto:
                print(f"Já existe uma ENTRADA em aberto para este funcionário em {data_marc}. Feche (Saída) antes de abrir outra.")
                return None

            novo_id = self.mongo.db["marcacoes"].count_documents({}) + 1

            # Inserção no MongoDB
            self.mongo.db["marcacoes"].insert_one({
                "id_marc": novo_id,
                "id_func": id_func,
                "data_marc": data_marc,
                "hora_entrada": hora_marc,
                "hora_saida": None,
                "tipo": "E"
            })

            marc = Marcacao(
                id_marc=novo_id,
                id_func=id_func,
                data_marc=data_marc,
                hora_marc=hora_marc,
                tipo="E"
            )
            print("Entrada registrada com sucesso!")
            print("  ", marc.to_string())
            return marc

        else:  # Tipo = "S"
            aberto = self._get_open_period(id_func, data_marc)
            if not aberto:
                print(f"Não há ENTRADA em aberto para {data_marc}. Registre a entrada antes da saída.")
                return None

            id_marc_aberto, hora_ent = aberto

            self.mongo.db["marcacoes"].update_one(
                {"id_marc": id_marc_aberto},
                {"$set": {"hora_saida": hora_marc}}
            )

            marc = Marcacao(
                id_marc=id_marc_aberto,
                id_func=id_func,
                data_marc=data_marc,
                hora_marc=hora_marc,
                tipo="S"
            )
            print("Saída registrada com sucesso!")
            print("  Entrada correspondente:", Marcacao(id_marc_aberto, id_func, data_marc, hora_ent, "E").to_string())
            print("  ", marc.to_string())
            return marc

    def atualizar_marcacao(self) -> Marcacao | None:
        self.mongo.connect()

        id_marc = int(input("ID da Marcação (período) que irá alterar: "))

        if self.verifica_existencia_marcacao(id_marc):
            nova_data = input("Nova Data (DD-MM-YYYY): ").strip()
            nova_hora_ent = input("Nova Hora de ENTRADA (HH:MM): ").strip()
            nova_hora_sai = input("Nova Hora de SAÍDA (HH:MM): ").strip()

            # Atualiza a marcação no MongoDB
            self.mongo.db["marcacoes"].update_one(
                {"id_marc": id_marc},
                {
                    "$set": {
                        "data_marc": nova_data,
                        "hora_entrada": nova_hora_ent,
                        "hora_saida": nova_hora_sai
                    }
                }
            )

            df = self.mongo.db["marcacoes"].find_one({"id_marc": id_marc})

            marc_E = Marcacao(
                id_marc=df["id_marc"],
                id_func=df["id_func"],
                data_marc=df["data_marc"],
                hora_marc=df["hora_entrada"],
                tipo="E"
            )
            marc_S = Marcacao(
                id_marc=df["id_marc"],
                id_func=df["id_func"],
                data_marc=df["data_marc"],
                hora_marc=df["hora_saida"],
                tipo="S"
            )

            print("Período atualizado com sucesso!")
            print("  ", marc_E.to_string())
            print("  ", marc_S.to_string())
            return marc_E
        else:
            print(f"O ID da marcação {id_marc} não existe.")
            return None

    def excluir_marcacao(self) -> None:
        self.mongo.connect()

        try:
            id_marc = int(input("ID da Marcação (período) que irá excluir: "))
        except ValueError:
            print("Entrada inválida.")
            return

        if not self.verifica_existencia_marcacao(id_marc):
            # Recupera os dados da marcação que será excluída
            df = self.mongo.db["marcacoes"].find_one({"id_marc": id_marc})

            # Apaga a marcação do MongoDB
            self.mongo.db["marcacoes"].delete_one({"id_marc": id_marc})

            marc_E = Marcacao(
                id_marc=df["id_marc"],
                id_func=df["id_func"],
                data_marc=df["data_marc"],
                hora_marc=df["hora_entrada"],
                tipo="E"
            )

            print("Período removido com sucesso!")
            print("  ", marc_E.to_string())

            # Só imprime a SAÍDA se houver hora
            hora_sai = df["hora_saida"]
            if hora_sai:
                marc_S = Marcacao(
                    id_marc=df["id_marc"],
                    id_func=df["id_func"],
                    data_marc=df["data_marc"],
                    hora_marc=hora_sai,
                    tipo="S"
                )
                print("  ", marc_S.to_string())
            else:
                print("  (sem saída registrada)")
        else:
            print(f"O ID da marcação {id_marc} não existe.")

    def verifica_existencia_marcacao(self, id_marc: int) -> bool:
        return self.mongo.db["marcacoes"].count_documents({"id_marc": id_marc}) == 0

    def verifica_existencia_funcionario(self, id_func: int) -> bool:
        return self.mongo.db["funcionarios"].count_documents({"id_func": id_func}) == 0