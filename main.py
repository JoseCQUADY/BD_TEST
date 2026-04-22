from datetime import datetime
from config.settings import DB_CONFIG, EXPORTS_DIR
from src.database_manager import DatabaseManager
from src.excel_generator import ExcelReportGenerator
from src.mail_service import MailService
from src.logger_manager import get_logger

log = get_logger("Main")

def run_automation():
    mailer = MailService()
    current_step = "System Initialization"
    log.info("Starting automation cycle.")

    try:
        current_step = "Database data extraction"
        db = DatabaseManager()
        result, connection = db.get_data_stream("logs_telefonia")

        current_step = "Excel file generation"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = EXPORTS_DIR / f"Report_{timestamp}.xlsx"
        
        generator = ExcelReportGenerator(str(report_path))
        generator.apply_branding()
        generator.write_data_as_table(result, DB_CONFIG['chunk_size'])
        generator.save()
        connection.close()

        current_step = "Business report delivery"
        if not mailer.send_report(str(report_path)):
            raise Exception("Operational mail delivery failed.")
        
        log.info("Automation cycle completed successfully.")

    except Exception as e:
        log.error(f"Critical failure during [{current_step}]: {e}", exc_info=True)
        mailer.send_error_alert(current_step)

if __name__ == "__main__":
    run_automation()