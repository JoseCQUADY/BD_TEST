import os
import gc
import json
import subprocess
import sys
from datetime import datetime
from config.settings import SOURCE_DATA_DIR, EXPORTS_DIR
from src.logger_manager import get_logger

log = get_logger("Main")

def run_automation():
    current_step = "System Initialization"
    log.info("Starting production file-to-pdf ETL automation workflow.")
    gc.collect()

    try:
        current_step = "Resolving execution timeframe parameters"
        runtime_clock = datetime.now()
        target_month = runtime_clock.month
        target_year = runtime_clock.year

        current_step = "Scanning date directories and tracking file chunks"
        from src.file_extractor import FileExtractor
        extractor = FileExtractor(SOURCE_DATA_DIR)
        
        # Extraemos los registros en una estructura temporal compacta de Python
        records = list(extractor.extract_chunks_for_month(target_month, target_year))
        del extractor
        gc.collect()

        current_step = "Generating stylized corporate pdf report table"
        timestamp = runtime_clock.strftime("%Y%m%d_%H%M%S")
        report_path = EXPORTS_DIR / f"Report_{timestamp}.pdf"
        
        # Serializamos los datos para el proceso hijo
        json_data = json.dumps(records)
        
        # Invocamos al subproceso hijo aislado
        worker_path = os.path.join(os.path.dirname(__file__), "src", "pdf_worker.py")
        process = subprocess.run(
            [sys.executable, worker_path, str(report_path), json_data],
            capture_output=True,
            text=True
        )
        
        # Limpieza inmediata de los strings de datos transferidos
        del json_data
        del records
        gc.collect()
        
        if process.returncode != 0:
            raise Exception(f"PDF isolated worker crashed with log: {process.stderr}")

        current_step = "Executing secure automated email distribution"
        from src.mail_service import MailService
        mailer = MailService()
        if not mailer.send_report(str(report_path)):
            raise Exception("Operational report delivery protocol failed via SMTP.")
        
        log.info("Automated network reporting sequence completed successfully.")

    except Exception as e:
        log.error(f"Critical execution break during step [{current_step}]: {e}", exc_info=True)
        from src.mail_service import MailService
        MailService().send_error_alert(current_step)

if __name__ == "__main__":
    run_automation()


