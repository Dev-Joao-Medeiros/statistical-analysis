<h1 align="center">Trabalho de Estatística - UFPA </h1>

<div align="center">
  <img width="400" height="200" alt="image" src="https://github.com/user-attachments/assets/a838ce3e-0347-4830-b642-9a6ada47bd0e" />
</div>


## Descrição
<p align = justify>
Repositório com código e resultados do trabalho de estatística, que possui o intuito de analizar banco de dados já existente, com população, preferencialmente, acima de 10.000 (dez mil) elementos,  para realizar tarefas relacionadas à população e suas amostras. Contém scripts, dados processados e outputs (planilhas e gráficos) organizados para reprodução.
</p>

## Dados usados

[Stack Overflow Annual Developer Survey 2024](https://www.kaggle.com/datasets/joebeachcapital/stack-overflow-annual-developer-survey-2024)

## Requisitos

- Python 3.8+
- Virtual environment (venv)
- Dependências listadas em `requirements.txt`

## Instalação (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Como usar

1. Ative o ambiente virtual (veja comando acima).
2. Execute o script principal:

```powershell
python main.py
```

3. Os resultados (planilhas, gráficos) serão gerados na pasta `resultados_estatistica/`.

## Estrutura do repositório

- `main.py` - ponto de entrada para execução das análises.
- `requirements.txt` - dependências do projeto.
- `resultados_estatistica/` - saída das análises (Excel, PNG, etc.).

## Boas práticas

- Use um ambiente virtual para isolar dependências.
- Versione apenas código e dados não sensíveis.
- Documente alterações importantes no `README.md` ou em um `CHANGELOG.md`.

## Contribuições

Pull requests são bem-vindos. Para contribuições maiores, abra primeiro uma issue descrevendo a proposta.

## Contato

Para dúvidas ou sugestões, adicione uma issue ou envie uma mensagem no repositório.
