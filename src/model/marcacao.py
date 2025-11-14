from datetime import datetime

DATE_FMT = "%d-%m-%Y" 
TIME_FMT = "%H:%M"

class Marcacao:
    """
    data_marc: 'DD-MM-YYYY'
    hora_marc: 'HH:MM'
    tipo: 'E' (entrada) ou 'S' (saída)
    """
    def __init__(self, id_marc, id_func, data_marc, hora_marc, tipo, nome_func=None):
        self.__id_marc = id_marc
        self.__id_func = id_func
        self.set_data_marc(data_marc)
        self.set_hora_marc(hora_marc)
        self.set_tipo(tipo)
        self.__nome_func = nome_func

    def get_id_marc(self):
        return self.__id_marc

    def get_id_func(self):
        return self.__id_func

    def get_data_marc(self):
        return self.__data_marc

    def get_hora_marc(self):
        return self.__hora_marc

    def get_tipo(self):
        return self.__tipo

    def get_nome_func(self):
        return self.__nome_func

    def set_id_marc(self, id_marc: int):
        self.__id_marc = id_marc

    def set_id_func(self, id_func: int):
        self.__id_func = id_func

    def set_data_marc(self, data_marc):
        try:
            self.__data_marc = datetime.strptime(str(data_marc), DATE_FMT).strftime(DATE_FMT) # normaliza o formato
        except ValueError:
            raise ValueError("Data inválida. Use o formato DD-MM-YYYY.")

    def set_hora_marc(self, hora_marc):
        try:
            self.__hora_marc = datetime.strptime(str(hora_marc), TIME_FMT).strftime(TIME_FMT) # normaliza o formato
        except ValueError:
            raise ValueError("Hora inválida. Use o formato HH:MM.")

    def set_tipo(self, tipo):
        t = str(tipo).strip().upper()[:1] #normaliza o tipo
        if t not in {"E", "S"}: # valida
            raise ValueError("Tipo inválido: use 'E' (entrada) ou 'S' (saída).") 
        self.__tipo = t

    def set_nome_func(self, nome_func):
        self.__nome_func = nome_func

    def __str__(self) -> str:
        nome = self.__nome_func or f"FUNC:{self.__id_func}" # se nome não estiver definido, mostra o id_func
        tipo_txt = "Entrada" if self.__tipo == "E" else "Saída" # mostra o tipo por extenso
        idtxt = self.__id_marc if self.__id_marc is not None else "—" # se id_marc for None, mostra um travessão
        return f"[{idtxt}] {nome} • {self.__data_marc} {self.__hora_marc} • {tipo_txt}" # formata a string

    def to_string(self) -> str:
        return str(self)
