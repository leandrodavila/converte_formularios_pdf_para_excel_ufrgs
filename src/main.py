import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from src.config import load_config
from src.sap_client import create_sap_client
from src.extractor import extract_form_data
from src.excel_generator import create_excel_report
from src.models import ExtractionResult


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Extração em lote de PDFs de formulários - Projeto Ancestralidades"
    )
    parser.add_argument(
        "pdf_folder",
        type=Path,
        help="Pasta contendo os PDFs para processar"
    )
    parser.add_argument(
        "--quilombo",
        type=str,
        help="Nome do quilombo (sobrescreve nome da pasta)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Caminho para arquivo de configuração (padrão: config.yaml)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ativar logging detalhado"
    )
    return parser.parse_args()


def setup_logging(level: int, output_dir: Path, log_filename: str) -> None:
    """
    Configure logging to console and file.

    Args:
        level: Logging level (DEBUG or INFO)
        output_dir: Directory for log files
        log_filename: Base log filename
    """
    # Create logs directory
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}_{log_filename}"

    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    # Set console handler level
    console_handler = logging.getLogger().handlers[1]
    console_handler.setLevel(level)


def resolve_quilombo(cli_arg: str | None, pdf_folder: Path) -> str:
    """
    Resolve quilombo value with priority: CLI > folder name.

    Args:
        cli_arg: --quilombo CLI argument (optional)
        pdf_folder: Path to folder containing PDFs

    Returns:
        Quilombo name to use for all records
    """
    if cli_arg:
        return cli_arg
    return pdf_folder.name


def main():
    """Main entry point"""

    # Parse arguments
    args = parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        sys.exit(1)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level, Path(config.output.directory), config.output.log_filename)
    logger = logging.getLogger(__name__)

    # Validate input folder
    if not args.pdf_folder.is_dir():
        logger.error(f"Pasta não encontrada: {args.pdf_folder}")
        sys.exit(1)

    pdfs = sorted(args.pdf_folder.glob("*.pdf"))
    if not pdfs:
        logger.error(f"Nenhum PDF encontrado em: {args.pdf_folder}")
        sys.exit(1)

    # Determine quilombo value
    quilombo = resolve_quilombo(args.quilombo, args.pdf_folder)
    logger.info(f"Quilombo: {quilombo}")

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(config.output.directory) / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório de saída: {output_dir}")

    # Initialize SAP client
    try:
        client = create_sap_client(config.sap, config.extraction)
        logger.info(f"✅ Conexão SAP AI Hub estabelecida (modelo: {config.sap.model_name})")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao SAP AI Hub: {e}")
        sys.exit(1)

    # Process PDFs
    logger.info(f"📂 {len(pdfs)} PDF(s) encontrado(s)\n")
    results: list[ExtractionResult] = []

    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"[{i}/{len(pdfs)}] {pdf_path.name} ...", end=" ", flush=True)

        result = extract_form_data(
            pdf_path=pdf_path,
            quilombo=quilombo,
            client=client,
            config=config
        )
        results.append(result)

        print("✅" if result.success else "❌")

        # Rate limiting
        if i < len(pdfs):
            time.sleep(config.extraction.rate_limit_delay)

    # Generate Excel report
    excel_path = output_dir / config.output.excel_filename
    create_excel_report(results, excel_path, config)
    logger.info(f"\n✅ Planilha salva em: {excel_path}")

    # Print summary
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    logger.info(f"   {successful}/{len(results)} participante(s) extraído(s) com sucesso")

    if failed > 0:
        logger.warning(f"   ⚠️  {failed} erro(s):")
        for result in results:
            if not result.success:
                logger.warning(f"      - {result.filename}: {result.error}")


if __name__ == "__main__":
    main()
