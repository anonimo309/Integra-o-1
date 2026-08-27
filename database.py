from sqlalchemy import (
    create_engine, Column, String, Float, Integer,
    DateTime, Date, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from config.settings import settings

Base = declarative_base()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class Canal(Base):
    __tablename__ = "canais"
    id         = Column(String, primary_key=True)   # meta_ads | clickup | vendedor | organico
    nome       = Column(String, nullable=False)
    tipo       = Column(String)                      # trafego_pago | vendedor | organico


class Vendedor(Base):
    __tablename__ = "vendedores"
    id         = Column(String, primary_key=True)
    nome       = Column(String, nullable=False)
    canal_id   = Column(String, ForeignKey("canais.id"))
    ativo      = Column(Integer, default=1)


class Campanha(Base):
    __tablename__ = "campanhas"
    id           = Column(String, primary_key=True)
    nome         = Column(String, nullable=False)
    canal_id     = Column(String, ForeignKey("canais.id"))
    objetivo     = Column(String)
    status       = Column(String)
    criada_em    = Column(DateTime)


class CustoCampanha(Base):
    """Gasto diário por campanha (Meta Ads)."""
    __tablename__ = "custos_campanha"
    __table_args__ = (UniqueConstraint("campanha_id", "data", name="uq_campanha_data"),)

    id           = Column(Integer, primary_key=True, autoincrement=True)
    campanha_id  = Column(String, ForeignKey("campanhas.id"))
    data         = Column(Date, nullable=False)
    gasto        = Column(Float, default=0)
    impressoes   = Column(Integer, default=0)
    cliques      = Column(Integer, default=0)
    leads        = Column(Integer, default=0)
    cpl          = Column(Float)        # custo por lead
    cpc          = Column(Float)
    cpm          = Column(Float)
    atualizado_em = Column(DateTime, default=datetime.utcnow)


class CustoDisparo(Base):
    """Custo de disparos WhatsApp API por dia e categoria."""
    __tablename__ = "custos_disparo"
    __table_args__ = (UniqueConstraint("data", "categoria", name="uq_disparo_data_cat"),)

    id           = Column(Integer, primary_key=True, autoincrement=True)
    data         = Column(Date, nullable=False)
    categoria    = Column(String)    # marketing | utility | authentication | service
    volume       = Column(Integer, default=0)
    custo_total  = Column(Float, default=0)
    custo_medio  = Column(Float)
    atualizado_em = Column(DateTime, default=datetime.utcnow)


class CustoManual(Base):
    """Custos manuais vindos do Excel."""
    __tablename__ = "custos_manuais"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    data         = Column(Date, nullable=False)
    canal        = Column(String)
    descricao    = Column(Text)
    valor        = Column(Float, nullable=False)
    importado_em = Column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id             = Column(String, primary_key=True)
    canal_id       = Column(String, ForeignKey("canais.id"))
    campanha_id    = Column(String, ForeignKey("campanhas.id"), nullable=True)
    vendedor_id    = Column(String, ForeignKey("vendedores.id"), nullable=True)
    status         = Column(String)
    data_criacao   = Column(DateTime)
    data_atualizacao = Column(DateTime)
    fonte_dados    = Column(String)    # clickup | sistema_proprio


class Venda(Base):
    __tablename__ = "vendas"

    id             = Column(String, primary_key=True)
    lead_id        = Column(String, ForeignKey("leads.id"), nullable=True)
    canal_id       = Column(String, ForeignKey("canais.id"))
    vendedor_id    = Column(String, ForeignKey("vendedores.id"), nullable=True)
    valor          = Column(Float, default=0)
    data_fechamento = Column(DateTime)
    status         = Column(String)


class MetricaCAC(Base):
    """CAC calculado por canal e período — tabela de resultado do BI."""
    __tablename__ = "metricas_cac"
    __table_args__ = (UniqueConstraint("periodo", "canal_id", name="uq_cac_periodo_canal"),)

    id               = Column(Integer, primary_key=True, autoincrement=True)
    periodo          = Column(Date, nullable=False)       # primeiro dia do mês
    canal_id         = Column(String, ForeignKey("canais.id"))
    total_investido  = Column(Float, default=0)
    total_clientes   = Column(Integer, default=0)
    cac              = Column(Float)                      # total_investido / total_clientes
    leads_gerados    = Column(Integer, default=0)
    taxa_conversao   = Column(Float)                      # clientes / leads
    calculado_em     = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso.")


if __name__ == "__main__":
    create_tables()
