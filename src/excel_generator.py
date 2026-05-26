import os
from datetime import datetime
import xlsxwriter
import pandas as pd
from config.settings import (
    COLOR_MUSTARD, COLOR_GRAY, COLOR_GRAY_LIGHT, 
    COLOR_BLACK, FONT_PRIMARY, FONT_SECONDARY, LOGO_PATH
)
from src.logger_manager import get_logger

log = get_logger("ExcelGenerator")

class ExcelReportGenerator:
    def __init__(self, filepath):
        self.filepath = filepath
        self.workbook = xlsxwriter.Workbook(filepath)
        self.worksheet = self.workbook.add_worksheet("Telephony Logs")
        self.worksheet.hide_gridlines(2)
        self._define_formats()

    def _define_formats(self):
        self.fmt_title = self.workbook.add_format({
            'bold': True, 'font_name': FONT_PRIMARY, 'font_size': 28,
            'font_color': COLOR_GRAY, 'align': 'center', 'valign': 'vcenter'
        })
        self.fmt_contact = self.workbook.add_format({
            'font_name': FONT_PRIMARY, 'font_size': 10,
            'font_color': COLOR_BLACK, 'align': 'center'
        })
        self.fmt_table_header = self.workbook.add_format({
            'bold': True, 'font_name': FONT_SECONDARY, 'font_size': 12,
            'font_color': '#FFFFFF', 'bg_color': COLOR_GRAY,
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': COLOR_GRAY
        })
        self.fmt_data = self.workbook.add_format({
            'font_name': FONT_SECONDARY, 'font_size': 10,
            'align': 'left', 'valign': 'vcenter'
        })
        self.fmt_total = self.workbook.add_format({
            'bold': True, 'font_name': FONT_SECONDARY, 'font_size': 11
        })
        self.fmt_note_title = self.workbook.add_format({
            'bold': True, 'font_name': FONT_SECONDARY, 'font_size': 12, 'font_color': COLOR_MUSTARD
        })
        self.fmt_note_text = self.workbook.add_format({
            'font_name': FONT_SECONDARY, 'font_size': 10, 'italic': True, 'text_wrap': True
        })

    def apply_header_design(self, num_cols):
        col_end = num_cols
        border_top = self.workbook.add_format({'top': 5, 'top_color': COLOR_MUSTARD})
        self.worksheet.merge_range(0, 1, 0, col_end, '', border_top)
        
        if os.path.exists(LOGO_PATH):
            self.worksheet.insert_image('B2', LOGO_PATH, {'x_scale': 0.5, 'y_scale': 0.5, 'y_offset': 10})

        self.worksheet.merge_range(1, 1, 3, col_end, "AVAYA ACRA", self.fmt_title)
        contact_text = "San Pedro Garza García, Nuevo León\n(81) 5000-2200 | correo@bancobase.com"
        self.worksheet.merge_range(4, 1, 5, col_end, contact_text, self.fmt_contact)
        self.worksheet.write('B8', 'REPORTE DE TELEFONÍA AVAYA ACRA', self.fmt_total)
        generation_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.worksheet.write('B9', f'Fecha de generación: {generation_time}', self.fmt_data)

    def write_data_stream(self, chunk_generator):
        start_row = 10
        start_col = 1
        current_row = start_row + 1
        total_records = 0
        headers = []
        column_widths = {}

        for chunk_df in chunk_generator:
            if chunk_df.empty:
                continue

            if total_records == 0:
                headers = [str(h).upper() for h in chunk_df.columns]
                num_cols = len(headers)
                self.apply_header_design(num_cols)
                
                for col_idx, header in enumerate(headers):
                    column_widths[col_idx] = len(header)
                    self.worksheet.write(start_row, start_col + col_idx, header, self.fmt_table_header)

            for _, row in chunk_df.iterrows():
                row_values = []
                for col_idx, val in enumerate(row):
                    string_value = str(val) if pd.notnull(val) else ""
                    row_values.append(string_value)
                    column_widths[col_idx] = max(column_widths[col_idx], len(string_value))
                
                self.worksheet.write_row(current_row, start_col, row_values, self.fmt_data)
                current_row += 1
                total_records += 1

        if total_records == 0:
            log.warning("Empty transaction stream detected. Writing empty dataset structure.")
            self.worksheet.write(start_row + 1, start_col, "SIN REGISTROS DISPONIBLES", self.fmt_total)
            return

        end_row = current_row - 1
        end_col = start_col + len(headers) - 1

        self.worksheet.add_table(start_row, start_col, end_row, end_col, {
            'columns': [{'header': h} for h in headers],
            'style': 'Table Style Light 1',
            'banded_rows': True
        })

        for col_idx, max_len in column_widths.items():
            self.worksheet.set_column(start_col + col_idx, start_col + col_idx, max_len + 5)

        self._write_footer(end_row + 2, start_col, end_col, total_records)

    def _write_footer(self, row_idx, start_col, end_col, count):
        self.worksheet.write(row_idx, start_col, f'TOTAL REGISTROS: {count}', self.fmt_total)
        row_idx += 3
        self.worksheet.write(row_idx, start_col, 'Nota de Confidencialidad:', self.fmt_note_title)
        self.worksheet.merge_range(row_idx + 1, start_col, row_idx + 2, end_col, 
            'Este documento contiene información técnica confidencial del sistema de telefonía exclusiva para personal de infraestructura.', 
            self.fmt_note_text)

        border_bottom = self.workbook.add_format({'bottom': 5, 'bottom_color': COLOR_MUSTARD})
        self.worksheet.merge_range(row_idx + 4, start_col, row_idx + 4, end_col, 
            'Reporte Generado Automáticamente', self.fmt_contact)
        self.worksheet.merge_range(row_idx + 5, start_col, row_idx + 5, end_col, '', border_bottom)

    def save(self):
        self.worksheet.freeze_panes(11, 0)
        self.workbook.close()