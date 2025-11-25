# Sistema de Controle de Ponto – Python + MongoDB

**Disciplina:** Banco de Dados

**Professor:** Howard Roatti

**Instituição:** FAESA

**Última atualização:** Novembro/2025

**Integrantes:** Hellen Karla Costa, Júlia Ogassavara, Yasmim Luiz

**Turma:** 4SC1

**Vídeo de Apresentação:** https://www.youtube.com/watch?v=1ww08wVKLtQ

---

## Descrição do Projeto

O **Sistema de Controle de Ponto** registra marcações de entrada/saída dos funcionários, calcula jornadas, controla atrasos/faltas e gera relatórios de presença e banco de horas.

Esta versão usa **MongoDB** (NoSQL) mantendo o modelo conceitual da versão em Oracle. Há um script de **migração** que lê as tabelas `LABDATABASE.FUNCIONARIOS` e `LABDATABASE.MARCACOES` no Oracle e grava documentos nas coleções `funcionarios` e `marcacoes` no MongoDB.

O sistema implementa operações de **consulta, inserção, atualização e remoção** para as entidades **Funcionário** e **Marcação**, além de relatórios via pipelines de agregação do MongoDB (equivalente a GROUP BY / JOIN).

---

## Requisitos do Ambiente

### Software necessário

- Python 3.10+
- MongoDB (rodando em `localhost:27017` por padrão)
- Arquivos de dependências: `requirements.txt`

Opcional (para migração):
- Banco Oracle acessível
- Oracle Instant Client configurado
- Usuário/schema `LABDATABASE` com as tabelas `FUNCIONARIOS` e `MARCACOES`

### Instalação das dependências

No diretório raiz do projeto, criar/ativar o ambiente virtual e instalar:

```bash
python3 -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r src/requirements.txt
```

Para sair do ambiente virtual:

```bash
deactivate
```

---

## Estrutura do projeto

```
src/
├─ conexion/
│  ├─ mongo_queries.py        # Classe MongoQueries (conexão MongoDB)
│  └─ oracle_queries.py       # Classe OracleQueries (usada na migração)
├─ controller/
│  ├─ controller_funcionario.py
│  └─ controller_marcacao.py
├─ model/
│  ├─ funcionario.py
│  └─ marcacao.py
├─ reports/
│  └─ relatorios.py
├─ utils/
│  ├─ config.py
│  └─ splash_screen.py
├─ createCollectionsAndData.py # Migração Oracle → MongoDB
└─ principal.py                # Ponto de entrada (CLI)
```

---

## Fluxo de Execução — Versão MongoDB

1) Clonar o repositório

```bash
git clone https://github.com/<seu_usuario>/<nome_do_repositorio>.git
cd <nome_do_repositorio>
```

2) Criar/ativar ambiente virtual e instalar dependências

```bash
python3 -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r src/requirements.txt
```

3) (Opcional) Migrar dados do Oracle para o MongoDB

Se o Oracle estiver disponível com o schema `LABDATABASE` e as tabelas já criadas:

- Ajuste os parâmetros de conexão (ex.: `conexion/passphrase/authentication.oracle`) com usuário/senha válidos.
- Entre em `src/` e rode o script de migração:

```bash
cd src
python createCollectionsAndData.py
```

O script:
- Cria (ou recria) as coleções `funcionarios` e `marcacoes` no MongoDB
- Lê os dados de `LABDATABASE.FUNCIONARIOS` e `LABDATABASE.MARCACOES` no Oracle
- Converte os registros para documentos JSON
- Insere os documentos no MongoDB

4) Executar o sistema principal

Dentro de `src/`:

```bash
python principal.py
```

O sistema abrirá um menu CLI com opções como:
- Relatórios
- Inserir registros
- Atualizar registros
- Remover registros
- Sair

As operações usam os controladores `controller_funcionario.py` e `controller_marcacao.py` para manipular dados.

---

## Exemplo de uso — `MongoQueries`

Exemplo de consulta simples (Python):

```python
from conexion.mongo_queries import MongoQueries

mongo = MongoQueries()
mongo.connect()

# lista de coleções disponíveis no banco configurado
print(mongo.db.list_collection_names())

# exemplo de leitura de todos os funcionários
cursor = mongo.db['funcionarios'].find({})
for doc in cursor:
    print(doc)

mongo.close()
```

Exemplo de inserção simples:

```python
from conexion.mongo_queries import MongoQueries

mongo = MongoQueries()
mongo.connect()

novo_funcionario = {
    'id_func': 999,
    'nome': 'Fulano de Tal',
    'cpf': '00000000000',
    'cargo': 'Analista de Teste'
}

mongo.db['funcionarios'].insert_one(novo_funcionario)
mongo.close()
```

---

## Solução de problemas comuns

### Erro: Authentication failed (MongoDB)

- Verifique se usuário/senha em `authentication.mongo` estão corretos.
- Confirme se o banco (padrão: `labdatabase`) existe e se o usuário tem permissão.
- Verifique se o MongoDB está rodando em `localhost:27017` ou ajuste `mongo_queries.py`.

### Erro: command listCollections requires authentication

- O servidor Mongo exige autenticação; ajuste `authentication.mongo` ou a configuração do servidor.

---

## Observações finais

- Esta versão explora conceitos de NoSQL (coleções, documentos JSON, pipelines de agregação) e a migração de um schema relacional (Oracle) para MongoDB.
- O foco é a integração Python + MongoDB e a manutenção da consistência do domínio de negócio.

