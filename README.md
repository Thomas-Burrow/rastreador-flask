# Um sistema para rastrear carros, agora em uma lingua mais accessivel
## Como Instalar (modo desenvolvimento)
1. Crie um venv e ative-lo como é customário para evitar problemas com depencias `python -m venv .venv; source .venv/bin/activate`
2. Instale as dependencias: `pip install -r requirements.txt`
3. Configure sua instalação de MariaDB (MySQL) e copie secrets-example/config.py para secrets/config.py, alterando os campos para refletir a configuração do banco de dados
4. Instale config.py em instance/ se vai executar os proximos comandos
5. Repita os ultimos dois passos para config-test.py para poder rodar pytest
6. Carregue o schema para o servidor SQL: `flask --app rastreador init-db`
7. Rode em modo desenvolvedor: `flask --app rastreador run --debug`

## Promovendo usuarios para podered acessar as paginas
1. Crie um usuario
2. `flask --app rastreador auth promote <usuario>`
3. Este usuario agora pode fazer tudo
4. Entre na pagina `/users` e mude o cargo de outros usuarios se nescessario

## Utilizando pre-commit
* Veja `https://pre-commit.com/` para mais informações
1. Com as dependencias instaladas e com o venv ativo, rode `pre-commit install`
2. Realize o commit e as ferramentas rodarão daquele ponto em diante.

## Servindo com gunicorn
* Veja [a documentação](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/) para mais informações
1. `gunicorn -c gunicorn_config.py rastreador:create_app()`