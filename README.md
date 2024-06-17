# Desafio de Data Engineer - EMD
___
Repositório de instrução para o desafio técnico para vaga de Pessoa Engenheira de Dados no Escritório de Dados do Rio de Janeiro

## Descrição do desafio
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

5. **Transformação com DBT**
   - Será criada uma tabela derivada utilizando DBT, que conterá o ID do ônibus, posição e velocidade.

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
```
git clone https://github.com/seu-usuario/repositorio-do-desafio.git
```
  
2. Crie um ambiente virtual utilizando `venv`:  
```
python -m venv venv
```

3. Ative o ambiente virtual:

- No Windows:

  ```
  venv\Scripts\activate
  ```

- No Linux/macOS:

  ```
  source venv/bin/activate
  ```

4. Instale as dependências do projeto:
```
pip install -r requirements.txt
```

5. Inicie o Docker e o PostgreSQL:
```
docker-compose up -d
```

6. Execute o arquivo `run.py` para iniciar a pipeline:
```
python run.py
```


