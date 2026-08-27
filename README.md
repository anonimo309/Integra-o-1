# BI de Aquisição de Clientes

Sistema de Business Intelligence para monitoramento do funil completo de aquisição — do primeiro contato até a venda finalizada.

## Fontes de dados

| Fonte | O que extrai |
|---|---|
| **ClickUp** | Pipeline de vendas, status dos deals, equipe comercial |
| **Meta Ads (Marketing API)** | Gasto por campanha, CPL, impressões, leads |
| **Meta WhatsApp (Cloud API)** | Custo e volume de disparos por categoria |
| **Sistema próprio** | Vendas finalizadas, leads, clientes convertidos |
| **Excel / Google Sheets** | Custos manuais e complementares |

## Métricas calculadas

- **CAC por canal** — Custo de Aquisição de Cliente segmentado por tráfego pago, vendedor e orgânico
- **CPL** — Custo por Lead por campanha
- **Custo de disparo** — Custo real de cada template WhatsApp enviado
- **CAC real** = custo mídia + custo disparo + custo equipe / clientes convertidos
- **Taxa de conversão** por vendedor e por canal
- **Performance individual** — leads atendidos, fechamentos, ticket médio por vendedor

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/bi-aquisicao.git
cd bi-aquisicao

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# edite o .env com suas credenciais

# 5. Criar tabelas no banco
python main.py setup
```

## Uso

```bash
# Sincronizar últimos 30 dias
python main.py etl --dias 30

# Sincronizar período específico
python main.py etl --inicio 2024-01-01 --fim 2024-01-31

# Iniciar dashboard
python main.py dashboard
```

## Estrutura do projeto

```
bi-aquisicao/
├── integrations/
│   ├── clickup/          # ClickUp API v2
│   ├── meta/             # Meta Marketing API + WhatsApp Cloud API
│   ├── excel/            # Leitura de .xlsx e Google Sheets
│   └── sistema_proprio/  # API do sistema de vendas
├── etl/
│   └── pipeline.py       # Orquestração do ETL
├── models/
│   ├── database.py       # Schema SQLAlchemy (PostgreSQL)
│   └── cac.py            # Motor de cálculo de CAC e métricas
├── dashboard/
│   └── app.py            # Streamlit dashboard
├── config/
│   └── settings.py       # Configurações centralizadas (Pydantic)
├── tests/                # Testes por módulo
├── .env.example          # Variáveis necessárias
├── requirements.txt
└── main.py               # Ponto de entrada
```

## Configuração das APIs

### Meta Cloud API
1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie um app do tipo **Business**
3. Adicione o produto **Marketing API** e **WhatsApp Business**
4. Gere um token de longa duração (60 dias) e adicione ao `.env`

### ClickUp
1. Acesse **ClickUp → Settings → Apps → API Token**
2. Copie o token e adicione ao `.env`
3. Identifique o `CLICKUP_LIST_ID` da sua lista de pipeline

### Sistema próprio
- Configure `SISTEMA_API_URL` e `SISTEMA_API_KEY` no `.env`
- Adapte os endpoints em `integrations/sistema_proprio/client.py`

## Licença

Privado — uso interno.
