# Desafio de Data Engineer - EMD
___
Repositório de instrução para o desafio técnico para vaga de Pessoa Engenheira de Dados no Escritório de Dados do Rio de Janeiro

## Descrição do Desafio
___
O desafio consiste em criar uma pipeline para capturar, estruturar, armazenar e transformar dados de uma API instantânea de GPS de ônibus BRT. Os dados devem ser coletados minuto a minuto, armazenados em um arquivo CSV e carregados em uma tabela PostgreSQL. Além disso, deve ser criada uma tabela derivada usando DBT, contendo o ID do ônibus, sua posição e velocidade.

## Solução Proposta
___
A solução agora é totalmente Dockerizada, o que significa que todo o processo é executado dentro de contêineres Docker. Isso simplifica a configuração e execução do projeto, pois o usuário só precisa ter o Docker instalado e pode iniciar o projeto com um único comando.

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
   - Utilizando uma instância Dockerizada do PostgreSQL, os dados do CSV serão carregados em uma tabela específica.

5. **Tabela Derivada com DBT**
   - A cada 10 minutos, a materialized view é atualizada na instância Dockerizada do Postgres.

### Requisitos
___
- Docker  


- **Docker Desktop para Windows:** https://docs.docker.com/desktop/install/windows-install/

### Execução do Projeto
___
Para executar o projeto, siga os passos abaixo:

1. Clone o repositório:  
    ```bash
    git clone https://github.com/NicolasEvilasio/emd-desafio-data-eng
    ```

2. Inicie o Docker:
    ```bash
    docker-compose --build -d
    ```

3. Aguarde a execução do código.
A partir do 10º minuto será criada uma tabela no postgres, chamada `brt_data` e uma materialized view, chamada `vw_brt_last_info`
- Clique aqui para abrir o arquivo vw_brt_last_info.sql  
- A view retornar os dados, garantindo que não há duplicidades e que é a informação mais atual:
- !Imagem do resultado da query da view vw_brt_last_info