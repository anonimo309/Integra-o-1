from datetime import datetime, timedelta, date
from loguru import logger

from integrations.clickup.client import ClickUpClient
from integrations.meta.client import MetaAdsClient, MetaWhatsAppClient
from integrations.sistema_proprio.client import SistemaProprioClient
from models.database import SessionLocal, CustoCampanha, CustoDisparo, Lead, Venda
from config.settings import settings


class ETLPipeline:
    def __init__(self):
        self.clickup = ClickUpClient()
        self.meta_ads = MetaAdsClient()
        self.meta_whatsapp = MetaWhatsAppClient()
        self.sistema = SistemaProprioClient()

    def run(self, data_inicio: date = None, data_fim: date = None):
        fim = data_fim or date.today()
        inicio = data_inicio or (fim - timedelta(days=settings.etl_lookback_days))

        logger.info(f"ETL iniciado | período: {inicio} → {fim}")

        self._sync_meta_ads(inicio, fim)
        self._sync_meta_whatsapp(inicio, fim)
        self._sync_clickup(inicio, fim)
        self._sync_sistema(inicio, fim)

        logger.info("ETL concluído com sucesso.")

    def _sync_meta_ads(self, inicio: date, fim: date):
        logger.info("Sincronizando Meta Ads...")
        try:
            records = self.meta_ads.get_campaign_insights(inicio, fim, level="campaign")
            with SessionLocal() as session:
                for r in records:
                    leads = next(
                        (int(a["value"]) for a in r.get("actions", []) if a["action_type"] == "lead"),
                        0,
                    )
                    custo = CustoCampanha(
                        campanha_id=r.get("campaign_id"),
                        data=date.fromisoformat(r.get("date_start")),
                        gasto=float(r.get("spend", 0)),
                        impressoes=int(r.get("impressions", 0)),
                        cliques=int(r.get("clicks", 0)),
                        leads=leads,
                        cpc=float(r.get("cpc", 0) or 0),
                        cpm=float(r.get("cpm", 0) or 0),
                    )
                    session.merge(custo)
                session.commit()
            logger.info(f"Meta Ads: {len(records)} registros salvos.")
        except Exception as e:
            logger.error(f"Erro ao sincronizar Meta Ads: {e}")

    def _sync_meta_whatsapp(self, inicio: date, fim: date):
        logger.info("Sincronizando Meta WhatsApp API...")
        try:
            analytics = self.meta_whatsapp.get_conversation_analytics(inicio, fim)
            with SessionLocal() as session:
                for a in analytics:
                    custo = CustoDisparo(
                        data=date.fromisoformat(a.get("start", str(inicio))),
                        categoria=a.get("conversation_type", "marketing"),
                        volume=a.get("conversation_count", 0),
                        custo_total=float(a.get("cost", 0)),
                    )
                    session.merge(custo)
                session.commit()
            logger.info(f"WhatsApp API: {len(analytics)} registros salvos.")
        except Exception as e:
            logger.error(f"Erro ao sincronizar WhatsApp API: {e}")

    def _sync_clickup(self, inicio: date, fim: date):
        logger.info("Sincronizando ClickUp...")
        try:
            dt_inicio = datetime.combine(inicio, datetime.min.time())
            tasks = self.clickup.get_all_tasks(date_updated_gt=dt_inicio)
            with SessionLocal() as session:
                for t in tasks:
                    lead = Lead(
                        id=t["id"],
                        status=t.get("status", {}).get("status", ""),
                        data_criacao=datetime.fromtimestamp(int(t.get("date_created", 0)) / 1000),
                        data_atualizacao=datetime.fromtimestamp(int(t.get("date_updated", 0)) / 1000),
                        fonte_dados="clickup",
                    )
                    session.merge(lead)
                session.commit()
            logger.info(f"ClickUp: {len(tasks)} tasks sincronizadas.")
        except Exception as e:
            logger.error(f"Erro ao sincronizar ClickUp: {e}")

    def _sync_sistema(self, inicio: date, fim: date):
        logger.info("Sincronizando sistema próprio...")
        try:
            dt_inicio = datetime.combine(inicio, datetime.min.time())
            dt_fim    = datetime.combine(fim,    datetime.min.time())

            vendas = self.sistema.get_vendas(dt_inicio, dt_fim)
            with SessionLocal() as session:
                for v in vendas:
                    venda = Venda(
                        id=str(v.get("id")),
                        canal_id=v.get("canal_origem"),
                        vendedor_id=str(v.get("vendedor_id")) if v.get("vendedor_id") else None,
                        valor=float(v.get("valor", 0)),
                        data_fechamento=datetime.fromisoformat(v.get("data_fechamento", dt_fim.isoformat())),
                        status=v.get("status", "concluida"),
                    )
                    session.merge(venda)
                session.commit()
            logger.info(f"Sistema próprio: {len(vendas)} vendas sincronizadas.")
        except Exception as e:
            logger.error(f"Erro ao sincronizar sistema próprio: {e}")
