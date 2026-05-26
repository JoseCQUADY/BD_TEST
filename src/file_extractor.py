import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.logger_manager import get_logger

log = get_logger("FileExtractor")

class FileExtractor:
    def __init__(self, root_directory):
        self.root_directory = Path(root_directory)
        self.date_pattern = re.compile(r"^\d{2}-\d{2}-\d{4}$")

    def extract_chunks_for_month(self, target_month, target_year):
        log.info(f"Starting memory-efficient directory scan for timeframe: {target_year}-{target_month:02d}")
        
        valid_folder_discovered = False

        for folder in self.root_directory.iterdir():
            if not folder.is_dir() or not self.date_pattern.match(folder.name):
                continue

            try:
                folder_date = datetime.strptime(folder.name, "%d-%m-%Y")
            except ValueError:
                log.warning(f"Skipping incorrectly formatted date folder structure: {folder.name}")
                continue

            if folder_date.month != target_month or folder_date.year != target_year:
                continue

            valid_folder_discovered = True
            log.info(f"Target chronological directory matched: {folder.name}")
            
            excel_files = [f for f in folder.iterdir() if f.is_file() and f.suffix in ['.xlsx', '.xls']]
            
            if not excel_files:
                log.warning(f"No executable spreadsheet files discovered inside directory: {folder.name}")
                continue
                
            if len(excel_files) > 1:
                raise ValueError(f"Ambiguity conflict in directory [{folder.name}]: Multiple data payloads detected.")

            target_file_path = excel_files[0]
            log.info(f"Streaming data stream from binary spreadsheet: {target_file_path.name}")
            
            try:
                raw_df = pd.read_excel(target_file_path, header=None)
                normalized_df = self._parse_structured_layout(raw_df)
                
                if not normalized_df.empty:
                    yield normalized_df
            except Exception as e:
                log.error(f"Critical operational failure deserializing data file: {target_file_path.name}")
                raise e

        if not valid_folder_discovered:
            raise FileNotFoundError(f"No matching operational target directories found for timeframe: {target_year}-{target_month:02d}")

    def _parse_structured_layout(self, dataframe):
        parsed_records = []
        
        current_employee = None
        current_id = None
        
        for _, row in dataframe.iterrows():
            row_values = [str(val).strip() if pd.notnull(val) else "" for val in row]
            
            employee_cell = ""
            for val in row_values:
                if val.startswith("Employee:"):
                    employee_cell = val
                    break
            
            if employee_cell:
                current_employee = employee_cell.replace("Employee:", "").strip()
                current_id = ""
                
                for val in row_values:
                    if "Employee ID:" in val:
                        current_id = val.split("Employee ID:")[-1].strip()
                        break
                continue

            if current_employee:
                start_date_value = ""
                
                for val in row_values:
                    if "/" in val and len(val) >= 8:
                        try:
                            datetime.strptime(val, "%m/%d/%Y")
                            start_date_value = val
                            break
                        except ValueError:
                            continue
                
                parsed_records.append({
                    "EMPLOYEE": current_employee,
                    "EMPLOYEE ID": current_id if current_id else "",
                    "START DATE": start_date_value
                })
                
                current_employee = None
                current_id = None

        return pd.DataFrame(parsed_records)