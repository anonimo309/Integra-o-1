from dataclasses import dataclass, field
from datetime import date
from typing import Optional
try:
    from loguru import logger
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("cac")


@dataclass
class ResultadoCAC:
    periodo: date
    canal: str
    total_investido: float
    total_clientes: int
    leads_gerados: int
    custo_midia: float = 0
    custo_disparo: float = 0
    custo_manual: float = 0

    @property
    def cac(self) -> Optional[float]:
        """CAC = investimento total / clientes convertidos."""
        if self.total_clientes == 0:
            return None
        return round(self.total_investido / self.total_clientes, 2)

    @property
    def cpl(self) -> Optional[float]:
        """Custo por lead = investimento / leads gerados."""
        if self.leads_gerados == 0:
            return None
        return round(self.total_investido / self.leads_gerados, 2)

    @property
    def taxa_conversao(self) -> Optional[float]:
        """Taxa de conversão lead → cliente (%)."""
        if self.leads_gerados == 0:
            return None
        return round((self.total_clientes / self.leads_gerados) * 100, 2)

    def resumo(self) -> dict:
        return {
            "periodo": self.periodo.isoformat(),
            "canal": self.canal,
            "custo_midia": self.custo_midia,
            "custo_disparo": self.custo_disparo,
            "custo_manual": self.custo_manual,
            "total_investido": self.total_investido,
            "leads_gerados": self.leads_gerados,
            "clientes_convertidos": self.total_clientes,
            "cac": self.cac,
            "cpl": self.cpl,
            "taxa_conversao_pct": self.taxa_conversao,
        }


class CalculadoraCAC:
    """
    Centraliza o cálculo de CAC, CPL e taxa de conversão
    unificando os custos de todas as fontes.
    """

    def calcular(
        self,
        periodo: date,
        canal: str,
        custo_midia: float,
        custo_disparo: float,
        custo_manual: float,
        total_clientes: int,
        leads_gerados: int,
    ) -> ResultadoCAC:
        total = custo_midia + custo_disparo + custo_manual

        resultado = ResultadoCAC(
            periodo=periodo,
            canal=canal,
            total_investido=round(total, 2),
            total_clientes=total_clientes,
            leads_gerados=leads_gerados,
            custo_midia=custo_midia,
            custo_disparo=custo_disparo,
            custo_manual=custo_manual,
        )

        logger.info(
            f"CAC calculado | {canal} | {periodo} | "
            f"investido: R${total:.2f} | clientes: {total_clientes} | "
            f"CAC: R${resultado.cac or 0:.2f}"
        )
        return resultado

    def calcular_por_vendedor(
        self,
        vendedor_id: str,
        vendedor_nome: str,
        periodo: date,
        custo_hora: float,
        horas_trabalhadas: float,
        leads_atendidos: int,
        vendas_fechadas: int,
    ) -> dict:
        """Calcula custo e performance por vendedor."""
        custo_total = custo_hora * horas_trabalhadas
        cac = round(custo_total / vendas_fechadas, 2) if vendas_fechadas > 0 else None
        taxa_conversao = round((vendas_fechadas / leads_atendidos) * 100, 2) if leads_atendidos > 0 else None

        return {
            "vendedor_id": vendedor_id,
            "vendedor_nome": vendedor_nome,
            "periodo": periodo.isoformat(),
            "custo_total": round(custo_total, 2),
            "leads_atendidos": leads_atendidos,
            "vendas_fechadas": vendas_fechadas,
            "cac": cac,
            "taxa_conversao_pct": taxa_conversao,
            "ticket_medio": None,  # calculado externamente com dados de valor das vendas
        }
