import os
import xlsxwriter
from datetime import datetime
from config.settings import COLOR_MUSTARD, COLOR_GRAY, COLOR_GRAY_LIGHT, COLOR_BLACK, FONT_PRIMARY, FONT_SECONDARY, LOGO_PATH
from src.logger_manager import get_logger

log = get_logger("ExcelGenerator")

class ExcelReportGenerator:
    def __init__(self, filepath):
        self.filepath = filepath
        self.workbook = xlsxwriter.Workbook(filepath)
        self.worksheet = self.workbook.add_worksheet("Telephony Logs")
        self.worksheet.hide_gridlines(2)

        # Format definition
        self.fmt_title = self.workbook.add_format({
            'bold': True, 'font_name': FONT_PRIMARY, 'font_size': 28,
            'font_color': COLOR_GRAY, 'align': 'center', 'valign': 'vcenter'
        })

        self.fmt_contact = self.workbook.add_format({
            'bold': True, 'font_name': FONT_PRIMARY, 'font_size': 11,
            'font_color': COLOR_BLACK, 'align': 'center'
        })

        self.fmt_header = self.workbook.add_format({
            'bold': True,
            'bg_color': COLOR_GRAY_LIGHT,
            'border': 1,
            'border_color': '#F5A800',
            'align': 'center'
        })

        self.fmt_table_header = self.workbook.add_format({
            'bold': True,
            'font_name': FONT_SECONDARY,
            'font_size': 14,
            'font_color': COLOR_GRAY,
            'bg_color': COLOR_GRAY_LIGHT,
            'border': 1,
            'border_color': COLOR_GRAY_LIGHT,
            'align': 'center',
            'valign': 'vcenter',
        })

        self.fmt_data = self.workbook.add_format({
            'font_name': FONT_SECONDARY, 'font_size': 11,
            'border': 1, 'border_color': COLOR_GRAY_LIGHT,
            'align': 'left'
        })

        self.fmt_total = self.workbook.add_format({
            'bold': True, 'font_name': FONT_SECONDARY, 'font_size': 11, 'align': 'left'
        })

        self.fmt_note_title = self.workbook.add_format({
            'bold': True, 'font_name': FONT_SECONDARY, 'font_size': 14, 'font_color': COLOR_MUSTARD
        })

        self.fmt_note_text = self.workbook.add_format({
            'font_name': FONT_SECONDARY, 'font_size': 11, 'italic': True, 'text_wrap': True
        })

    def apply_design(self, num_cols):

        border_top = self.workbook.add_format({'top': 5, 'top_color': COLOR_MUSTARD})
        border_bottom = self.workbook.add_format({'bottom': 5, 'bottom_color': COLOR_MUSTARD})

        col_start = 2
        col_end = num_cols + 1

        self.worksheet.write_blank('B1', '', border_top)
        self.worksheet.merge_range(0, col_start, 0, col_end, '', border_top)

        # Logo
        if os.path.exists(LOGO_PATH):
            self.worksheet.insert_image('B3', LOGO_PATH, {'x_scale': 0.6, 'y_scale': 0.6})

        # bank title
        self.worksheet.merge_range(1, 2, 3, num_cols + 1, "BANCO BASE", self.fmt_title)

        # Contact info
        self.worksheet.merge_range(4, 2, 4, num_cols + 1,
                                   "San Pedro Garza García, Nuevo León",
                                   self.fmt_contact)

        self.worksheet.merge_range(5, 2, 5, num_cols + 1,
                                   "(81) 5000-2200 | correo@bancobase.com",
                                   self.fmt_contact)

        # report title
        self.worksheet.write('B8', 'REPORTE DE TELEFONÍA AVAYA ACRA', self.fmt_total)

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.worksheet.write('B9', f'Fecha: {fecha}')

    def write_data(self, db_result, chunk_size=500):
        headers = [h.upper() for h in db_result.keys()]
        num_cols = len(headers)

        col_start = 2
        col_end = num_cols + 1

        self.apply_design(num_cols)

        header_row = 10
        self.worksheet.set_row(header_row, 30)

        col_widths = [(len(h) * 2) + 2 for h in headers]

        for i, h in enumerate(headers):
            self.worksheet.write(header_row, i + 1, h, self.fmt_table_header)

        row_idx = header_row + 1
        count = 0
        has_data = False

        # Chunks
        while True:
            rows = db_result.fetchmany(chunk_size)
            if not rows:
                break

            has_data = True

            for row in rows:
                for col_idx, val in enumerate(row):
                    text = str(val) if val is not None else ""
                    self.worksheet.write(row_idx, col_idx + 1, text, self.fmt_data)

                new_width = (len(text) * 1.1) + 1
                if new_width > col_widths[col_idx]:
                    col_widths[col_idx] = min(new_width, 50)

                row_idx += 1
                count += 1

        for i, width in enumerate(col_widths):
            self.worksheet.set_column(i + 1, i + 1, width)

        # Case: without records
        if not has_data:
            self.worksheet.merge_range(
                row_idx, 1, row_idx + 2, num_cols,
                "SIN REGISTROS DISPONIBLES EN EL SISTEMA",
                self.fmt_no_data
            )
            row_idx += 3

        for i, width in enumerate(col_widths):
            self.worksheet.set_column(i + 1, i + 1, width)

        # Footer
        row_idx += 1
        self.worksheet.merge_range(
            row_idx, 1, row_idx, num_cols,
            f'TOTAL REGISTROS: {count}',
            self.fmt_total
        )

        row_idx += 3
        self.worksheet.write(row_idx, 1, 'Nota de Confidencialidad:', self.fmt_note_title)

        self.worksheet.merge_range(
            row_idx + 1, 1, row_idx + 2, num_cols,
            'Este documento contiene información técnica confidencial del sistema de telefonía exclusiva para personal de infraestructura.',
            self.fmt_note_text
        )

        row_idx += 4
        self.worksheet.merge_range(
            row_idx, 1, row_idx, num_cols,
            'Reporte Generado Automáticamente',
            self.fmt_contact
        )

        border_bottom = self.workbook.add_format({'bottom': 5, 'bottom_color': COLOR_MUSTARD})
        self.worksheet.write_blank(row_idx + 2, 1, '', border_bottom)
        self.worksheet.merge_range(
            row_idx + 2, col_start, row_idx + 2, col_end, '', border_bottom
        )

    def save(self):
        self.worksheet.freeze_panes(11, 0)
        self.workbook.close()