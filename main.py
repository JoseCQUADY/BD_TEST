from datetime import datetime
from config.settings import SOURCE_DATA_DIR, EXPORTS_DIR
from src.file_extractor import FileExtractor
from src.pdf_generator import PdfReportGenerator
from src.mail_service import MailService
from src.logger_manager import get_logger

log = get_logger("Main")

def run_automation():
    mailer = MailService()
    current_step = "System Initialization"
    log.info("Starting production file-to-pdf ETL automation workflow.")

    try:
        current_step = "Resolving execution timeframe parameters"
        runtime_clock = datetime.now()
        target_month = runtime_clock.month
        target_year = runtime_clock.year

        current_step = "Scanning date directories and tracking file chunks"
        extractor = FileExtractor(SOURCE_DATA_DIR)
        data_stream = extractor.extract_chunks_for_month(target_month, target_year)

        current_step = "Generating stylized corporate pdf report table"
        timestamp = runtime_clock.strftime("%Y%m%d_%H%M%S")
        report_path = EXPORTS_DIR / f"Report_{timestamp}.pdf"
        
        generator = PdfReportGenerator(str(report_path))
        generator.write_data_stream(data_stream)
        generator.save()

        current_step = "Executing secure automated email distribution"
        if not mailer.send_report(str(report_path)):
            raise Exception("Operational report delivery protocol failed via SMTP.")
        
        log.info("Automated network reporting sequence completed successfully.")

    except Exception as e:
        log.error(f"Critical execution break during step [{current_step}]: {e}", exc_info=True)
        mailer.send_error_alert(current_step)

if __name__ == "__main__":
    run_automation()