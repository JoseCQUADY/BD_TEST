import xlsxwriter
from datetime import datetime
from config.settings import COLOR_MUSTARD, LOGO_PATH
from src.logger_manager import get_logger

log = get_logger("ExcelGenerator")

class ExcelReportGenerator:
    def __init__(self, filepath):
        self.filepath = filepath
        self.workbook = xlsxwriter.Workbook(filepath)
        self.worksheet = self.workbook.add_worksheet("Telephony Logs")
        
        self.header_format = self.workbook.add_format({
            'bold': True, 
            'bg_color': COLOR_MUSTARD, 
            'border': 1, 
            'align': 'center'
        })
        self.data_format = self.workbook.add_format({'border': 1})

    def apply_branding(self):
        if LOGO_PATH.exists():
            self.worksheet.insert_image('A1', str(LOGO_PATH), {'x_scale': 0.4, 'y_scale': 0.4})
        self.worksheet.write('C1', 'BANCO BASE', self.header_format)

    def write_data_as_table(self, db_result, chunk_size):
        log.info("Writing data to Excel table format.")
        headers = db_result.keys()
        columns_config = [{'header': h.upper()} for h in headers]
        
        start_row = 4
        current_row = 5
        total_records = 0
        
        while True:
            chunks = db_result.fetchmany(chunk_size)
            if not chunks:
                break
            for row in chunks:
                for col_idx, value in enumerate(row):
                    self.worksheet.write(current_row, col_idx, str(value), self.data_format)
                current_row += 1
            total_records += len(chunks)
        
        if total_records > 0:
            self.worksheet.add_table(
                start_row, 0, current_row - 1, len(headers) - 1, 
                {
                    'columns': columns_config,
                    'style': 'Table Style Light 14',
                    'name': 'GeneralReport'
                }
            )
            
            for i in range(len(headers)):
                self.worksheet.set_column(i, i, 20)
                
            log.info(f"Writing completed. Total records: {total_records}")

    def save(self):
        self.workbook.close()