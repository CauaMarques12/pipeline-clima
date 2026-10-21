# Pipeline ETL de dados climáticos 

Pipeline de Engenharia de Dados que coleta condições meteorológicas  na API OpenWeatherMap, transforma as respostas com pandas e armazena os resultados no PostgreSQL. A execução é orquestrada pelo Apache Airflow, com agendamento a cada hora e serviços executados em Docker Compose.

Projeto de estudo e portfólio.

## Fluxo dos dados





<img width="1983" height="793"  alt="Arquitetura do pipeline ETL" src="https://github.com/user-attachments/assets/87b47e1b-39f4-4469-a513-590c841bc61f" />






1. **Extract:** consulta a API e salva a resposta em `data/weather_data.json`.
2. **Transform:** normaliza os campos aninhados, remove e renomeia colunas e converte os timestamps para `America/Sao_Paulo`. Na DAG, o resultado é salvo em `data/temp_data.parquet`.
3. **Load:** lê o Parquet e adiciona os registros à tabela `mg_clima` no PostgreSQL.

Entre os dados coletados estão temperatura, sensação térmica, umidade, pressão, vento, nebulosidade, coordenadas e horários de nascer e pôr do sol.

## Tecnologias

| Tecnologia | Uso no projeto |
| --- | --- |
| Python 3.12+ | Extração, transformação e carga |
| Apache Airflow 3.1.7 | Agendamento, dependências e acompanhamento das tasks |
| Docker e Docker Compose | Execução dos serviços do Airflow |
| PostgreSQL | Armazenamento dos dados climáticos e dos metadados do Airflow, em bancos separados |
| pandas | Normalização e transformação dos dados |
| requests | Requisições à API OpenWeatherMap |
| SQLAlchemy e psycopg2 | Conexão e escrita no PostgreSQL |
| python-dotenv | Leitura das variáveis de ambiente |
| Parquet / PyArrow | Arquivo intermediário entre transformação e carga |
| uv | Gerenciamento do ambiente Python local |

O ambiente usado no desenvolvimento tem PostgreSQL separado para os dados climáticos. O serviço `postgres` do Compose usa PostgreSQL 16 para os metadados do Airflow.

## Estrutura

```text
pipeline-clima/
├── dags/
│   └── clima_dag.py         # DAG e definição das tasks
├── src/
│   ├── extract_data.py      # Requisição à API e gravação do JSON
│   ├── transform_data.py    # Transformações com pandas
│   └── load_data.py         # Carga no PostgreSQL
├── notebooks/
│   └── analysis_data.ipynb  # Notebook de análise
├── config/                 # Configurações locais, fora do Git
├── data/                   # JSON e Parquet gerados, fora do Git
├── logs/                   # Logs do Airflow, fora do Git
├── plugins/                # Diretório de plugins do Airflow
├── .env                    # Configuração local do Compose, fora do Git
├── docker-compose.yaml
├── main.py                 # Execução sequencial sem Airflow, para testes
├── pyproject.toml
└── uv.lock
```

## Como executar com Airflow

Os exemplos abaixo usam **Windows e PowerShell**, com Docker Desktop em execução e PostgreSQL instalado no Windows. A configuração do Compose é destinada ao desenvolvimento local.

### 1. Pré-requisitos

- Git e Docker Desktop com Docker Compose v2.
- Pelo menos 4 GB de memória disponíveis para o Docker; preferencialmente 8 GB, conforme o [guia oficial do Airflow](https://airflow.apache.org/docs/apache-airflow/3.1.7/howto/docker-compose/index.html).
- PostgreSQL local em execução na porta `5432`.
- Uma chave da API [OpenWeatherMap](https://openweathermap.org/api).
- Python e uv são necessários apenas para executar o pipeline fora do Airflow.

### 2. Clone e prepare as pastas

```powershell
git clone https://github.com/CauaMarques12/pipeline-clima.git
cd pipeline-clima
New-Item -ItemType Directory -Force -Path config,data,logs,plugins | Out-Null
```

### 3. Prepare o banco de dados para armazenar os dados climáticos

Conecte-se ao PostgreSQL do Windows:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres
```

Crie o banco, se ele ainda não existir:

```sql
CREATE DATABASE pipeline_clima;
```

Saia com `\q`. A tabela `mg_clima` é criada pela carga caso ainda não exista e o usuário tenha permissão.


### 4. Configure as variáveis locais

Crie `config/.env` com os nomes usados pelo código, em letras minúsculas:

```dotenv
api_key=SUA_CHAVE_OPENWEATHERMAP
user=SEU_USUARIO_POSTGRESQL
password=SUA_SENHA_POSTGRESQL
database=pipeline_clima
```

Crie também um arquivo `.env` na **raiz do projeto**, usado pelo Docker Compose:

```dotenv
AIRFLOW_UID=50000
```

Para uma imagem com dependências fixadas, consulte a [documentação de extensão da imagem do Airflow](https://airflow.apache.org/docs/apache-airflow/3.1.7/howto/docker-compose/index.html#using-custom-images).

Os dois arquivos `.env` estão ignorados pelo Git. Não publique sua chave da API nem sua senha.

### 5. Inicialize e suba os serviços

```powershell
docker compose up -d
docker compose ps
```

O Compose inclui API server, scheduler, DAG processor, worker, triggerer, Redis e o PostgreSQL de metadados.

### 6. Execute a DAG

1. Abra [http://localhost:8080](http://localhost:8080).
2. Entre com usuário `airflow` e senha `airflow`, caso não tenha alterado os valores padrão.
3. Localize a DAG **`clima_dag`** e retire-a do estado pausado.
4. Use **Trigger DAG** para uma execução manual ou aguarde o agendamento.
5. Acompanhe as tasks `extract`, `transform` e `load` e seus logs.

A DAG usa `0 */1 * * *`, executando no início de cada hora, com `catchup=False`. Estão configuradas até duas novas tentativas, com intervalo de cinco minutos, para tasks que lançarem exceções.

### 7. Consulte os dados

```powershell
psql -h localhost -p 5432 -U postgres -d pipeline_clima
```

```sql
SELECT COUNT(*) FROM mg_clima;

SELECT city_name, datetime, temperature, humidity
FROM mg_clima
ORDER BY datetime DESC
LIMIT 10;
```

## Conexão entre Docker e PostgreSQL

O código em `src/load_data.py` usa `host.docker.internal` para alcançar o PostgreSQL instalado no Windows a partir do container. Dentro de um container, `localhost` aponta para o próprio container.

O serviço `postgres` do Compose guarda **os metadados do Airflow**. Os dados meteorológicos são enviados para o banco `pipeline_clima` do PostgreSQL local, conforme as credenciais de `config/.env`.

## Execução sem Airflow

Para executar `main.py` diretamente no Windows, são necessários ajustes na configuração atual:

1. Em `src/load_data.py`, use `host = 'localhost'` para o PostgreSQL local.
2. Em `main.py`, use `Path(__file__).resolve().parent / 'config' / '.env'` para carregar o arquivo dentro do projeto. O caminho atual usa `parent.parent`.
3. Instale as dependências e execute na raiz:

```powershell
uv venv
uv pip install pandas requests sqlalchemy psycopg2-binary python-dotenv
uv run --no-project python main.py
```

Essa execução chama as três etapas sequencialmente, sem agendamento e sem o Parquet intermediário da DAG. Ao voltar para o Airflow, restaure o host para `host.docker.internal`.

## Diagnóstico rápido

| Situação | O que verificar |
| --- | --- |
| DAG não aparece | Consulte `docker compose logs airflow-dag-processor` e verifique erros de importação. |
| API retorna erro | Confira `api_key` em `config/.env` e a resposta da OpenWeatherMap. |
| Falha de conexão com PostgreSQL | Confira serviço local, porta, host, credenciais e acesso do Docker ao banco pelo firewall e pelas regras do PostgreSQL. |
| Erro ao gravar ou ler Parquet | Verifique se `pyarrow` está instalado no ambiente do worker. |

Para acompanhar a execução:

```powershell
docker compose logs --tail 100 airflow-worker
docker compose logs --tail 100 airflow-scheduler
```

<img width="1872" height="943" alt="exemplo com captura de tela da dag executada com sucesso" src="https://github.com/user-attachments/assets/4b2871ac-98a0-4618-9637-76c278de8d04" />



## Encerrar o ambiente

```powershell
docker compose stop
```

Para remover os containers e a rede, preservando o volume de metadados:

```powershell
docker compose down
```

