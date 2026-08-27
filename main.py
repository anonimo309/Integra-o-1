#!/usr/bin/env python3
"""
BI de Aquisição de Clientes
Ponto de entrada principal — executa o ETL e inicia o dashboard.
"""
import argparse
from datetime import date, timedelta
from loguru import logger
from models.database import create_tables
from etl.pipeline import ETLPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="BI de Aquisição de Clientes")
    subparsers = parser.add_subparsers(dest="command")

    # Comando: etl
    etl_parser = subparsers.add_parser("etl", help="Executar pipeline de sincronização")
    etl_parser.add_argument("--inicio", type=date.fromisoformat, help="Data início (YYYY-MM-DD)")
    etl_parser.add_argument("--fim",    type=date.fromisoformat, help="Data fim (YYYY-MM-DD)")
    etl_parser.add_argument("--dias",   type=int, default=30,   help="Janela em dias (padrão: 30)")

    # Comando: setup
    subparsers.add_parser("setup", help="Criar tabelas no banco de dados")

    # Comando: dashboard
    subparsers.add_parser("dashboard", help="Iniciar dashboard Streamlit")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "setup":
        logger.info("Criando tabelas no banco de dados...")
        create_tables()

    elif args.command == "etl":
        fim    = args.fim    or date.today()
        inicio = args.inicio or (fim - timedelta(days=args.dias))
        logger.info(f"Executando ETL: {inicio} → {fim}")
        pipeline = ETLPipeline()
        pipeline.run(inicio, fim)

    elif args.command == "dashboard":
        import subprocess
        logger.info("Iniciando dashboard Streamlit...")
        subprocess.run(["streamlit", "run", "dashboard/app.py"])

    else:
        logger.warning("Nenhum comando especificado. Use: setup | etl | dashboard")
        logger.info("Exemplo: python main.py etl --dias 30")


if __name__ == "__main__":
    main()
