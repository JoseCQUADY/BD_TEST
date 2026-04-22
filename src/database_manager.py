from sqlalchemy import create_engine, text
from config.settings import DB_CONFIG
from src.logger_manager import get_logger

log = get_logger("Database")

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DB_CONFIG['url'])

    def get_data_stream(self, table_name):
        try:
            log.info(f"Establishing connection for table: {table_name}")
            connection = self.engine.connect()
            query = text(f"SELECT * FROM {table_name}")
            result = connection.execution_options(stream_results=True).execute(query)
            log.info("Connection established. Streaming started.")
            return result, connection
        except Exception as e:
            log.error("Database connection interrupted.")
            raise e