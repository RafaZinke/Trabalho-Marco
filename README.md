# ME07: OpenAI + PandasAI + camada semântica

Fluxo: ME07 ou Supabase → DataFrame → `pai.create()` com metadados → `dataset.chat()` conectado à API da OpenAI → número, tabela ou gráfico.

## Executar no Windows

1. Instale Python **3.11**. Extraia o pacote e coloque `ME07(2).xlsx` na pasta dos arquivos Python.
2. Execute `py -3.11 -m venv .venv` e `.\.venv\Scripts\Activate.ps1`.
3. Execute `python -m pip install -r requirements.txt`.
4. Copie `.env.example` para `.env`; coloque sua chave em `OPENAI_API_KEY`. A assinatura do ChatGPT não substitui uma chave da API OpenAI. Não publique o `.env`.
5. Execute `streamlit run inteligencia.py`; selecione **Planilha local** e uma aba.

## Camada semântica

O arquivo `semantic_config.json` define o conjunto de dados e as descrições das colunas. Nomes de coluna são normalizados para minúsculas, sem acentos ou espaços. Confira os nomes exibidos no aplicativo e preencha, por exemplo:

```json
{
  "description": "Uma linha por registro ...",
  "columns": {
    "situacao": {"type": "string", "description": "Situação do registro; valores possíveis ..."},
    "valor": {"type": "float", "description": "Valor em reais ..."}
  }
}
```

Colunas sem definição usam tipo inferido e uma descrição provisória. Confirme a unidade de análise, as dimensões e as medidas reais da ME07. A aplicação usa a camada semântica nativa do PandasAI, por meio de `pai.create()`.

## Supabase

Obtenha a URI PostgreSQL no painel do projeto Supabase, preencha `DATABASE_URL` no `.env` e execute `python importar_supabase.py`. Passe o nome de outra aba como argumento, se necessário. A importação **substitui** a tabela `DB_TABLE` após confirmação. Depois escolha **Supabase** no aplicativo. Esse modo lê a tabela e usa o mesmo DataFrame semântico; não executa o SQL gerado no banco.

Para demonstrar, mostre a aba e as colunas, o dicionário semântico, uma pergunta tabular e outra pedindo um gráfico. Não mostre a chave da API na gravação.

O uso da API OpenAI e a conexão com o seu Supabase dependem das credenciais e de teste no seu ambiente.
