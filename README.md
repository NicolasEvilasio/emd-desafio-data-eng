# Desafio de Data Engineer - EMD
___
Repositório de instrução para o desafio técnico para vaga de Pessoa Engenheira de Dados no Escritório de Dados do Rio de Janeiro

## Descrição do Desafio
___
O desafio consiste em criar uma pipeline para capturar, estruturar, armazenar e transformar dados de uma API instantânea de GPS de ônibus BRT. Os dados devem ser coletados minuto a minuto, armazenados em um arquivo CSV e carregados em uma tabela PostgreSQL. Além disso, deve ser criada uma tabela derivada usando DBT, contendo o ID do ônibus, sua posição e velocidade.

## Solução Proposta
___
### Passos da Solução

1. **Captura de Dados**
   - A API de GPS do BRT será consultada a cada minuto.
   - Os dados serão armazenados temporariamente em memória, em um dataframe.

2. **Estruturação dos Dados**
   - Os dados serão estruturados conforme necessário para atender aos requisitos de armazenamento e transformação.

3. **Armazenamento em CSV**
   - A cada 10 minutos, os dados capturados serão consolidados em um arquivo CSV.
   - Um novo arquivo CSV será gerado a cada intervalo de 10 minutos.

4. **Armazenamento no PostgreSQL**
   - Utilizando uma instância local do PostgreSQL (Dockerizada), os dados do CSV serão carregados em uma tabela específica.

5. **Tabela Derivada com DBT**
   - A cada 10 minutos, a materialized view é atualizada na instância local do Postgres (Dockerizada).

### Requisitos
___
- Python 3.9
- pip
- PostgreSQL
- Docker
- Venv

### Execução do Projeto
___
Para executar o projeto, siga os passos abaixo:

1. Clone o repositório:  
    ```bash
    git clone https://github.com/NicolasEvilasio/emd-desafio-data-eng
    ```

2. Crie um ambiente virtual utilizando `venv`:  
    ```bash
    python -m venv venv
    ```

3. Ative o ambiente virtual:

    - No Windows:
      ```bash
      venv\Scripts\activate
      ```
    
    - No Linux/macOS:
      ```bash
      source venv/bin/activate
      ```

4. Instale as dependências do projeto:
    ```bash
    pip install -r requirements.txt
    ```

5. Crie um arquivo `.env` na pasta root do projeto, com o seguinte formato:  
    Altere os dados conforme sua necessidade.
    ```env
    DB_HOST=localhost
    DB_PORT=5400
    DB_USER=user
    DB_PASSWORD=password
    DB_DATABASE=mydb
    ```

6. Inicie o Docker e o PostgreSQL:
    ```bash
    docker-compose up -d
    ```

7. Execute o arquivo `run.py` para iniciar a pipeline:
    ```bash
    python run.py
    ```

8. Aguarde a execução do código.
A partir do 10º minuto será criada uma tabela no postgres, chamada `brt_data` e uma materialized view, chamada `vw_brt_last_info`
- Clique [aqui](https://github.com/NicolasEvilasio/emd-desafio-data-eng/blob/master/dbt_brt/models/mart/vw_brt_last_info.sql) para abrir o arquivo vw_brt_last_info.sql  
- A view retornar os dados, garantindo que não há duplicidades e que é a informação mais atual:
- ![Imagem do resultado da query da view vw_brt_last_info](imgs/vw_brt_last_info.png)
- 