# Sistema de Controle de Ponto – Python + MongoDB

**Disciplina:** Banco de Dados
**Professor:** Howard Roatti
**Instituição:** FAESA
**Última atualização:** Novembro/2025

**Integrantes: Hellen Karla Costa, Júlia Ogassavara e Yasmim Luiz**
**Turma: 4SC1**

---
## Descrição do Projeto

O **Sistema de Controle de Ponto** tem como objetivo registrar as marcações de entrada e saída dos funcionários, calcular jornadas de trabalho, controlar atrasos/faltas e gerar relatórios de presença e banco de horas.

Nesta versão, o projeto foi adaptado para utilizar o **MongoDB** como banco de dados **NoSQL**, mantendo o mesmo modelo conceitual da versão anterior em **Oracle**.Além disso, existe um script de **migração de dados** que lê as tabelas LABDATABASE.FUNCIONARIOS e LABDATABASE.MARCACOES no Oracle e grava os documentos equivalentes nas coleções funcionarios e marcacoes no MongoDB.

O sistema implementa operações de **consulta, inserção, atualização e remoção** sobre as entidades **Funcionário** e **Marcação**, além de relatórios baseados em **agregação** (pipeline) do MongoDB, equivalentes aos relatórios com GROUP BY e JOIN da versão relacional.

---
## Requisitos do Ambiente

### Software Necessário

**Python 3.10+** instalado no sistema;    
**MongoDB** instalado e em execução (padrão: localhost:27017);    
*   requirements.txt   
*   (Opcional – para migração):   
    - **Banco de Dados Oracle** acessível;
    - **Oracle Instant Client** configurado; 
     Usuário/schema LABDATABASE com as tabelas FUNCIONARIOS e MARCACOES.
        
### Instalação das Dependências

No diretório raiz do projeto:
`   python3 -m venv .venv  source .venv/bin/activate  pip install -r requirements.txt   `

Para sair do ambiente virtual depois:
`  deactivate   `

---
## Estrutura do Projeto

├── src/
│   ├── conexion/
│   │   ├── mongo_queries.py          # Classe MongoQueries (conexão MongoDB)
│   │   └── oracle_queries.py         # Classe OracleQueries (usada na migração)
│   ├── controller/
│   │   ├── controller_funcionario.py # Regras e operações de Funcionário
│   │   └── controller_marcacao.py    # Regras e operações de Marcação de ponto
│   ├── model/
│   │   ├── funcionario.py            # Classe de domínio Funcionário
│   │   └── marcacao.py               # Classe de domínio Marcação
│   ├── reports/
│   │   └── relatorios.py             # Relatórios em cima das coleções MongoDB
│   ├── utils/
│   │   ├── config.py                 # Menus, textos e utilidades gerais
│   │   └── splash_screen.py          # Tela inicial (totais de registros)
│   ├── createCollectionsAndData.py   # Migração Oracle → Mongo (coleções + dados)
│   ├── principal.py                  # Ponto de entrada da aplicação (CLI)
└── README.md

---
## Fluxo de Execução – Versão MongoDB

### 1\. Clonar o repositório
  ```bash
   git clone https://github.com/<seu_usuario>/<nome_do_repositorio>.git
   cd <nome_do_repositorio>
   ```
### 2\. Criar/ativar ambiente virtual e instalar dependências
 ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r src/requirements.txt
   ```
    
### 3\. (Opcional) Migrar dados do Oracle para o MongoDB
Se o banco Oracle estiver disponível com o schema LABDATABASE e as tabelas já criadas:

1.  Ajustar conexion/passphrase/authentication.oracle com usuário/senha válidos.    
2.  cd srcpython3 createCollectionsAndData.py
   
Este script:
*   Cria (ou recria) as coleções funcionarios e marcacoes no MongoDB;
*   Lê os dados de LABDATABASE.FUNCIONARIOS e LABDATABASE.MARCACOES no Oracle;    
*   Converte os registros para documentos JSON;    
*   Insere na base MongoDB.    

### 4\. Executar o sistema principal
Dentro de src/:
 ```bash
   python principal.py
   ```

O sistema abrirá um **menu de linha de comando (CLI)** com opções do tipo:
*   Relatórios    
*   Inserir registros  
*   Atualizar registros    
*   Remover registros   
*   Sair    

As operações utilizam os controladores (controller\_funcionario.py e controller\_marcacao.py) para acessar e manipular os dados de funcionários e marcações.

---
## Exemplo de Uso – MongoQueries

### Consulta simples
`  from conexion.mongo_queries import MongoQueries  mongo = MongoQueries()  mongo.connect()  # lista de coleções disponíveis no banco configurado  print(mongo.db.list_collection_names())  # exemplo de leitura de todos os funcionários  cursor = mongo.db["funcionarios"].find({})  for doc in cursor:      print(doc)  mongo.close()   `

### Inserção simples
`  from conexion.mongo_queries import MongoQueries  mongo = MongoQueries()  mongo.connect()  novo_funcionario = {      "id_func": 999,      "nome": "Fulano de Tal",      "cpf": "00000000000",      "cargo": "Analista de Teste"  }  mongo.db["funcionarios"].insert_one(novo_funcionario)  mongo.close()   `

---
## Solução de Problemas Comuns

### Erro: Authentication failed (MongoDB)

*   Verifique se o usuário e senha no arquivo authentication.mongo estão corretos.    
*   Confirme se o banco configurado (por padrão, labdatabase) realmente existe e se o usuário tem permissão sobre ele.    
*   Verifique se o MongoDB está rodando na porta 27017 em localhost (ou ajuste o host/porta em mongo\_queries.py).    

### Erro: command listCollections requires authentication
*   O servidor Mongo está exigindo autenticação, mas a conexão foi feita sem usuário/senha válidos.   
*   Ajuste authentication.mongo e/ou a configuração de segurança do MongoDB.
    
---
## Observações Finais

*   Esta versão MongoDB reutiliza o mesmo domínio de negócio da C2 (Oracle), mas explora conceitos de **banco de dados NoSQL**, **coleções**, **documentos JSON** e **pipelines de agregação**.    
*   O foco está tanto na **integração Python + MongoDB** quanto na **migração de dados** entre um banco relacional (Oracle) e um NoSQL (MongoDB), mantendo a consistência da aplicação de controle de ponto.
