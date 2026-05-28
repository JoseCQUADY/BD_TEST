import os
import gc
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
        data_stream = extractor.extract_chunks_for_month(target_month, target_year)

        current_step = "Initializing target PDF report path"
        timestamp = runtime_clock.strftime("%Y%m%d_%H%M%S")
        report_path = EXPORTS_DIR / f"Report_{timestamp}.pdf"
        
        current_step = "Instantiating corporate PDF report engine"
        from src.pdf_generator import PdfReportGenerator
        generator = PdfReportGenerator(str(report_path))
        
        current_step = "Streaming rows into the PDF generator canvas"
        for idx, chunk in enumerate(data_stream):
            generator.write_data_stream([chunk])
            
            del chunk
            
            if idx % 500 == 0:
                gc.collect()
        
        current_step = "Compiling and saving final PDF document to storage"
        generator.save()
        
        log.info("ETL processing phase finished. Releasing data pipeline structures from RAM.")
        del generator
        del extractor
        del data_stream
        gc.collect()

        current_step = "Executing secure automated email distribution"
        from src.mail_service import MailService
        mailer = MailService()
        
        if not mailer.send_report(str(report_path)):
            raise RuntimeError("Operational report delivery protocol failed via SMTP.")
        
        log.info("Automated network reporting sequence completed successfully.")

    except Exception as e:
        log.error(f"Critical execution break during step [{current_step}]: {e}", exc_info=True)
        
        try:
            from src.mail_service import MailService
            MailService().send_error_alert(current_step)
        except Exception as alert_error:
            log.critical(f"Emergency alert dispatch failure: {alert_error}")

if __name__ == "__main__":
    run_automation()


