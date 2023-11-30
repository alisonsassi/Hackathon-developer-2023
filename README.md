# **Projeto Hackathon-developer-2023**

O projeto Hackathon-developer-2023 visa abordar um desafio significativo enfrentado pelos Product Owners (P.O.s) das equipes, que frequentemente se deparam com a tarefa de redigir critérios de aceitação para as User Stories. Atualmente, essa é uma questão problemática na empresa, impactando a clareza para os desenvolvedores e dificultando o trabalho dos QA.

## Configuração do Azure

Para utilizar este projeto, é necessário configurar as credenciais do Azure no arquivo `azure_config.py`. Substitua as variáveis pelos valores correspondentes:

```python
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

class AzureConfig:
    org_url = 'YOUR_URL_ORGANIZATION_OF_AZURE'  # Ex: 'https://dev.azure.com/YourOrganization'
    token = 'YOUR_TOKEN_OF_AZURE'
    project_id = 'PROJECT_OF_AZURE'  # Ex: 'YourProject'
Configuração da API OpenAI
```


Além disso, insira a chave de API da OpenAI no mesmo arquivo:

```python
class OpenIA:
    api_key = "YOUR_TOKEN_OF_OPENAI"
```

## Instalação

Siga os passos abaixo para configurar o ambiente e instalar as dependências:

Crie um ambiente virtual:

``` bash
python -m venv venv
```

* Ative o ambiente virtual:

No Windows:
```bash
source venv\Scripts\activate
```

No Linux/Mac:

```bash
source venv/bin/activate
```

* Instale as dependências:

```bash
pip install -r requirements.txt
```
* Execução

Para executar o projeto, utilize os seguintes comandos:

Ative o ambiente virtual:

No Windows:
``` bash
source venv\Scripts\activate
```

No Linux/Mac:

```bash
source venv/bin/activate
```

Inicie o servidor Uvicorn:

```bash

uvicorn main:app --reload
```

A aplicação estará disponível para uso após essas etapas. Certifique-se de substituir todas as variáveis pelos valores apropriados para garantir a correta integração com o Azure DevOps e a API OpenAI.