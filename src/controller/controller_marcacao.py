from model.marcacao import Marcacao
from conexion.oracle_queries import OracleQueries

def _esc(s: str) -> str:
    return str(s).replace("'", "''")

class Controller_Marcacao:
    def __init__(self):
        pass

    def _resolve_funcionario(self, oracle: OracleQueries, entrada: str) -> int | None:
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
            if self.verifica_existencia_funcionario(oracle, id_func):  # True se NÃO existe
                print(f"O ID do funcionário {id_func} não existe. Cadastre o funcionário primeiro.")
                return None
            return id_func

        nome = _esc(entrada)
        df = oracle.sqlToDataFrame(f"""
            SELECT CODIGO_FUNCIONARIO AS id_func, NOME
              FROM LABDATABASE.FUNCIONARIOS
             WHERE UPPER(NOME) LIKE UPPER('%{nome}%')
             ORDER BY NOME
        """)

        if df.empty:
            print(f"Nenhum funcionário encontrado com nome contendo: {entrada}")
            return None
        if len(df) == 1:
            return int(df.id_func.values[0])

        print("Foram encontrados vários funcionários:")
        for _, row in df.iterrows():
            print(f"  {int(row['id_func'])} - {row['NOME']}")
        try:
            escolhido = int(input("Digite o ID exato do funcionário: ").strip())
        except ValueError:
            print("Entrada inválida.")
            return None

        if self.verifica_existencia_funcionario(oracle, escolhido):
            print(f"O ID {escolhido} não existe entre os resultados.")
            return None
        return escolhido

    def _get_open_period(self, oracle: OracleQueries, id_func: int, data_marc: str):
        df = oracle.sqlToDataFrame(f"""
            SELECT CODIGO_MARCACAO AS id_marc,
                   TO_CHAR(HORA_ENTRADA,'HH24:MI') AS hora_ent
              FROM LABDATABASE.MARCACOES
             WHERE CODIGO_FUNCIONARIO = {id_func}
               AND TRUNC(DATA_MARCACAO) = TO_DATE('{_esc(data_marc)}','DD-MM-YYYY')
               AND HORA_ENTRADA IS NOT NULL
               AND HORA_SAIDA   IS NULL
             ORDER BY CODIGO_MARCACAO DESC
             FETCH FIRST 1 ROWS ONLY
        """)
        if df.empty:
            return None
        return int(df.id_marc.values[0]), df.hora_ent.values[0]

    def inserir_marcacao(self) -> Marcacao | None:
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        entrada = input("Funcionário (ID ou Nome): ")
        id_func = self._resolve_funcionario(oracle, entrada)
        if id_func is None:
            return None

        tipo = input("Tipo (E=Entrada, S=Saída): ").strip().upper()[:1]
        if tipo not in {"E", "S"}:
            print("Tipo inválido. Use 'E' ou 'S'.")
            return None

        data_marc = _esc(input("Data (DD-MM-YYYY): ").strip())
        hora_marc = _esc(input("Hora (HH:MM): ").strip())

        if tipo == "E":
            aberto = self._get_open_period(oracle, id_func, data_marc)
            if aberto:
                print(f"Já existe uma ENTRADA em aberto para este funcionário em {data_marc}. Feche (Saída) antes de abrir outra.")
                return None


            seq_df = oracle.sqlToDataFrame("""
                SELECT LABDATABASE.MARCACOES_CODIGO_MARCACAO_SEQ.NEXTVAL AS id FROM DUAL
            """)
            novo_id = int(seq_df["id"].iloc[0])

            oracle.write(f"""
                INSERT INTO LABDATABASE.MARCACOES
                    (CODIGO_MARCACAO, DATA_MARCACAO, HORA_ENTRADA, HORA_SAIDA, CODIGO_FUNCIONARIO)
                VALUES
                    ({novo_id},
                     TO_DATE('{data_marc}','DD-MM-YYYY'),
                     TO_DATE('{data_marc} {hora_marc}','DD-MM-YYYY HH24:MI'),
                     NULL,
                     {id_func})
            """)

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

        else:  
            aberto = self._get_open_period(oracle, id_func, data_marc)
            if not aberto:
                print(f"Não há ENTRADA em aberto para {data_marc}. Registre a entrada antes da saída.")
                return None

            id_marc_aberto, hora_ent = aberto


            oracle.write(f"""
                UPDATE LABDATABASE.MARCACOES
                   SET HORA_SAIDA = TO_DATE('{data_marc} {hora_marc}','DD-MM-YYYY HH24:MI')
                 WHERE CODIGO_MARCACAO = {id_marc_aberto}
            """)

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
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        id_marc = int(input("ID da Marcação (período) que irá alterar: "))

        if not self.verifica_existencia_marcacao(oracle, id_marc):  # False se existe
            nova_data     = _esc(input("Nova Data (DD-MM-YYYY): ").strip())
            nova_hora_ent = _esc(input("Nova Hora de ENTRADA (HH:MM): ").strip())
            nova_hora_sai = _esc(input("Nova Hora de SAÍDA   (HH:MM): ").strip())

            oracle.write(f"""
                UPDATE LABDATABASE.MARCACOES
                   SET DATA_MARCACAO = TO_DATE('{nova_data}','DD-MM-YYYY'),
                       HORA_ENTRADA  = TO_DATE('{nova_data} {nova_hora_ent}', 'DD-MM-YYYY HH24:MI'),
                       HORA_SAIDA    = TO_DATE('{nova_data} {nova_hora_sai}', 'DD-MM-YYYY HH24:MI')
                 WHERE CODIGO_MARCACAO = {id_marc}
            """)

            df = oracle.sqlToDataFrame(f"""
                SELECT
                    CODIGO_MARCACAO                      AS id_marc,
                    CODIGO_FUNCIONARIO                   AS id_func,
                    TO_CHAR(DATA_MARCACAO, 'DD-MM-YYYY') AS data_marc,
                    TO_CHAR(HORA_ENTRADA,  'HH24:MI')    AS hora_ent,
                    TO_CHAR(HORA_SAIDA,    'HH24:MI')    AS hora_sai
                FROM LABDATABASE.MARCACOES
                WHERE CODIGO_MARCACAO = {id_marc}
            """)


            marc_E = Marcacao(
                id_marc=df.id_marc.values[0],
                id_func=df.id_func.values[0],
                data_marc=df.data_marc.values[0],
                hora_marc=df.hora_ent.values[0],
                tipo="E"
            )
            marc_S = Marcacao(
                id_marc=df.id_marc.values[0],
                id_func=df.id_func.values[0],
                data_marc=df.data_marc.values[0],
                hora_marc=df.hora_sai.values[0],
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
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        try:
            id_marc = int(input("ID da Marcação (período) que irá excluir: "))
        except ValueError:
            print("Entrada inválida.")
            return

        if not self.verifica_existencia_marcacao(oracle, id_marc):
            df = oracle.sqlToDataFrame(f"""
                SELECT
                    CODIGO_MARCACAO                      AS id_marc,
                    CODIGO_FUNCIONARIO                   AS id_func,
                    TO_CHAR(DATA_MARCACAO, 'DD-MM-YYYY') AS data_marc,
                    TO_CHAR(HORA_ENTRADA,  'HH24:MI')    AS hora_ent,
                    TO_CHAR(HORA_SAIDA,    'HH24:MI')    AS hora_sai
                FROM LABDATABASE.MARCACOES
                WHERE CODIGO_MARCACAO = {id_marc}
            """)

            # Apague antes de imprimir, como você já fazia
            oracle.write(f"DELETE FROM LABDATABASE.MARCACOES WHERE CODIGO_MARCACAO = {id_marc}")

            # Sempre imprime a ENTRADA
            marc_E = Marcacao(
                id_marc=df.id_marc.values[0],
                id_func=df.id_func.values[0],
                data_marc=df.data_marc.values[0],
                hora_marc=df.hora_ent.values[0],
                tipo="E"
            )

            print("Período removido com sucesso!")
            print("  ", marc_E.to_string())

            # Só imprime a SAÍDA se houver hora
            hora_sai = df.hora_sai.values[0]
            if hora_sai is not None and str(hora_sai).strip():
                marc_S = Marcacao(
                    id_marc=df.id_marc.values[0],
                    id_func=df.id_func.values[0],
                    data_marc=df.data_marc.values[0],
                    hora_marc=hora_sai,
                    tipo="S"
                )
                print("  ", marc_S.to_string())
            else:
                print("  (sem saída registrada)")
        else:
            print(f"O id_marc {id_marc} não existe.")


    def verifica_existencia_marcacao(self, oracle: OracleQueries, id_marc: int) -> bool:
        df = oracle.sqlToDataFrame(f"""
            SELECT 1 AS existe
              FROM LABDATABASE.MARCACOES
             WHERE CODIGO_MARCACAO = {id_marc}
        """)
        return df.empty

    def verifica_existencia_funcionario(self, oracle: OracleQueries, id_func: int) -> bool:
        df = oracle.sqlToDataFrame(f"""
            SELECT 1 AS existe
              FROM LABDATABASE.FUNCIONARIOS
             WHERE CODIGO_FUNCIONARIO = {id_func}
        """)
        return df.empty