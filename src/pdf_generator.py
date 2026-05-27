import os
from datetime import datetime
from src.logger_manager import get_logger

log = get_logger("PdfGenerator")

class PdfReportGenerator:
    def __init__(self, filepath):
        from fpdf import FPDF
        from config.settings import LOGO_PATH
        
        self.filepath = filepath
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=25)
        self.pdf.add_page()
        
        self.total_records = 0
        self.headers_written = False
        
        self._hex_mustard = (245, 168, 0)
        self._hex_gray = (111, 114, 113)
        self._hex_gray_light = (234, 236, 240)
        
        self.pdf.set_draw_color(*self._hex_mustard)
        self.pdf.set_line_width(1.5)
        self.pdf.line(15, 10, 195, 10)
        
        self.pdf.ln(5)
        if os.path.exists(LOGO_PATH):
            self.pdf.image(LOGO_PATH, x=15, y=14, w=30)
            
        self.pdf.set_font("Helvetica", "B", 24)
        self.pdf.set_text_color(*self._hex_gray)
        self.pdf.cell(180, 15, "AVAYA ACRA", ln=True, align="C")
        
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(0, 0, 0)
        contact_info = "San Pedro Garza García, Nuevo León  |  (81) 5000-2200  |  correo@bancobase.com"
        self.pdf.cell(180, 5, contact_info, ln=True, align="C")
        self.pdf.ln(10)
        
        self.pdf.set_font("Helvetica", "B", 11)
        self.pdf.cell(180, 6, "REPORTE DE TELEFONÍA AVAYA ACRA", ln=True, align="L")
        
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(*self._hex_gray)
        generation_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.pdf.cell(180, 5, f"Fecha de generación: {generation_time}", ln=True, align="L")
        self.pdf.ln(5)

    def write_data_stream(self, chunk_generator):
        col_widths = [90, 45, 45]
        
        for record in chunk_generator:
            if not self.headers_written:
                self.pdf.set_fill_color(*self._hex_gray)
                self.pdf.set_text_color(255, 255, 255)
                self.pdf.set_draw_color(*self._hex_gray)
                self.pdf.set_line_width(0.2)
                self.pdf.set_font("Helvetica", "B", 9)
                
                headers = ["EMPLOYEE", "EMPLOYEE ID", "START DATE"]
                for i, header in enumerate(headers):
                    self.pdf.cell(col_widths[i], 8, header, border=1, align="L", fill=True)
                self.pdf.ln(8)
                self.headers_written = True

            if self.total_records % 2 == 0:
                self.pdf.set_fill_color(249, 250, 235)
            else:
                self.pdf.set_fill_color(255, 255, 255)
                
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.set_font("Helvetica", "", 9)
            self.pdf.set_draw_color(*self._hex_gray_light)
            
            row_values = [record["EMPLOYEE"], record["EMPLOYEE ID"], record["START DATE"]]
            
            for i, val in enumerate(row_values):
                self.pdf.cell(col_widths[i], 7, val, border=1, align="L", fill=True)
            self.pdf.ln(7)
            
            self.total_records += 1

    def save(self):
        self.pdf.ln(5)
        self.pdf.set_font("Helvetica", "B", 10)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(180, 6, f"TOTAL REGISTROS: {self.total_records}", ln=True, align="L")
        self.pdf.ln(5)
        
        self.pdf.set_font("Helvetica", "B", 10)
        self.pdf.set_text_color((245, 168, 0))
        self.pdf.cell(180, 6, "Nota de Confidencialidad:", ln=True, align="L")
        
        self.pdf.set_font("Helvetica", "I", 8.5)
        self.pdf.set_text_color((111, 114, 113))
        note_text = "Este documento contiene información técnica confidencial del sistema de telefonía exclusiva para personal de infraestructura."
        self.pdf.cell(180, 5, note_text, ln=True, align="L")
        self.pdf.ln(10)
        
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color((111, 114, 113))
        self.pdf.cell(180, 5, "Reporte Generado Automáticamente", ln=True, align="C")
        
        self.pdf.set_draw_color(245, 168, 0)
        self.pdf.set_line_width(1.5)
        current_y = self.pdf.get_y() + 2
        self.pdf.line(15, current_y, 195, current_y)
        
        self.pdf.output(self.filepath)


