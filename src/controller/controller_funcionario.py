from model.funcionario import Funcionario
from conexion.oracle_queries import OracleQueries

def _esc(s: str) -> str:
    return str(s).replace("'", "''")

class Controller_Funcionario:
    def __init__(self):
        pass

    def inserir_funcionario(self) -> Funcionario | None:
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        nome = _esc(input("Nome: ").strip())
        cpf  = _esc(input("CPF (somente números): ").strip())
        cargo = _esc(input("Cargo: ").strip())

        seq_df = oracle.sqlToDataFrame("""
            SELECT LABDATABASE.FUNCIONARIOS_CODIGO_FUNCIONARIO_SEQ.NEXTVAL AS id FROM DUAL
        """)
        novo_id = int(seq_df["id"].iloc[0])

 
        oracle.write(f"""
            INSERT INTO LABDATABASE.FUNCIONARIOS (CODIGO_FUNCIONARIO, NOME, CPF, CARGO)
            VALUES ({novo_id}, '{nome}', '{cpf}', '{cargo}')
        """)

        df = oracle.sqlToDataFrame(f"""
            SELECT 
                CODIGO_FUNCIONARIO AS id_func,
                NOME               AS nome,
                CPF                AS cpf,
                CARGO              AS cargo
            FROM LABDATABASE.FUNCIONARIOS
            WHERE CODIGO_FUNCIONARIO = {novo_id}
        """)

        novo = Funcionario(
            df.id_func.values[0],
            df.nome.values[0],
            df.cpf.values[0],
            df.cargo.values[0]
        )
        print("Funcionário inserido com sucesso!")
        print(novo.to_string())
        return novo

    def atualizar_funcionario(self) -> Funcionario | None:
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        id_func = int(input("ID do Funcionário que irá alterar: "))

        if not self.verifica_existencia_funcionario(oracle, id_func):
            novo_nome  = _esc(input("Nome: ").strip())
            novo_cargo = _esc(input("Cargo: ").strip())

            oracle.write(f"""
                UPDATE LABDATABASE.FUNCIONARIOS
                   SET NOME  = '{novo_nome}',
                       CARGO = '{novo_cargo}'
                 WHERE CODIGO_FUNCIONARIO = {id_func}
            """)

            df = oracle.sqlToDataFrame(f"""
                SELECT 
                    CODIGO_FUNCIONARIO AS id_func,
                    NOME               AS nome,
                    CPF                AS cpf,
                    CARGO              AS cargo
                FROM LABDATABASE.FUNCIONARIOS
                WHERE CODIGO_FUNCIONARIO = {id_func}
            """)

            atualizado = Funcionario(
                df.id_func.values[0],
                df.nome.values[0],
                df.cpf.values[0],
                df.cargo.values[0]
            )
            print("Funcionário atualizado com sucesso!")
            print(atualizado.to_string())
            return atualizado
        else:
            print(f"O id_func {id_func} não existe.")
            return None

    def excluir_funcionario(self) -> None:
        oracle = OracleQueries(can_write=True)
        oracle.connect()

        id_func = int(input("ID do Funcionário que irá excluir: "))

        if not self.verifica_existencia_funcionario(oracle, id_func):

            df = oracle.sqlToDataFrame(f"""
                SELECT 
                    CODIGO_FUNCIONARIO AS id_func,
                    NOME               AS nome,
                    CPF                AS cpf,
                    CARGO              AS cargo
                FROM LABDATABASE.FUNCIONARIOS
                WHERE CODIGO_FUNCIONARIO = {id_func}
            """)

            oracle.write(f"""
                DELETE FROM LABDATABASE.FUNCIONARIOS
                WHERE CODIGO_FUNCIONARIO = {id_func}
            """)

            excluido = Funcionario(
                df.id_func.values[0],
                df.nome.values[0],
                df.cpf.values[0],
                df.cargo.values[0]
            )
            print("Funcionário removido com sucesso!")
            print(excluido.to_string())
        else:
            print(f"O id_func {id_func} não existe.")

    def verifica_existencia_funcionario(self, oracle: OracleQueries, id_func: int) -> bool:
        df = oracle.sqlToDataFrame(f"""
            SELECT 1 AS existe
              FROM LABDATABASE.FUNCIONARIOS
             WHERE CODIGO_FUNCIONARIO = {id_func}
        """)
        return df.empty
