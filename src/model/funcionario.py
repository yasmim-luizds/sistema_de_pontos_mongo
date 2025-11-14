import re # para validação de CPF, aqui ele limpa os caracteres e valida

class Funcionario:
    def __init__(self, id_func, nome, cpf, cargo):
        self.__id_func = id_func
        self.__nome = nome
        self.set_cpf(cpf)  # valida e normaliza
        self.__cargo = cargo

    def get_id_func(self):
        return self.__id_func

    def get_nome(self):
        return self.__nome

    def get_cpf(self):
        return self.__cpf

    def get_cargo(self):
        return self.__cargo

    def set_id_func(self, id_func: int):
        self.__id_func = id_func

    def set_nome(self, nome: str):
        self.__nome = nome

    def set_cpf(self, cpf: str):
        limpo = re.sub(r"[^0-9]", "", str(cpf)) # remove tudo que não for dígito
        if not self.validar_cpf(limpo):
            raise ValueError("CPF inválido.") 
        self.__cpf = limpo

    def set_cargo(self, cargo: str):
        self.__cargo = cargo

    def validar_cpf(self, cpf: str) -> bool:
        if len(cpf) != 11 or cpf == cpf[0] * 11: # sequências repetidas não são válidas (ex: 111.111.111-11)
            return False
        for i in range(9, 11): # valida os dois dígitos verificadores (numeros finais do cpf) e garante que o cpf é válido
            soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i)) # soma ponderada dos dígitos para cálculo do dígito verificador
            digito = ((soma * 10) % 11) % 10 # cálculo do dígito verificador
            if int(cpf[i]) != digito: # se o dígito verificador não bater, cpf inválido
                return False
        return True

    def __str__(self):
        return f"[{self.__id_func}] {self.__nome} • CPF: {self.__cpf} • Cargo: {self.__cargo}"

    def to_string(self) -> str:
        return str(self)




