import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError, DataError, IntegrityError
import logging
from src.entities.DataUnloading import DataUnloading
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class UploadResult(BaseModel):
    rows_loaded: int
    rows_failed: int

def process(file: UploadFile) -> UploadResult:
    try:
        df = pd.read_excel(file.file)
        logger.info(f"Excel file loaded: {file.filename}, {df.shape[0]} rows")
    except Exception as e:
        logger.error(f"Ошибка чтения Excel: {e}")
        raise ValueError(f"Не удалось прочитать Excel: {e}")

    # Сохраняем файл в data/ с уникальным именем
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла
    import uuid
    unique_name = f"{uuid.uuid4()}_{file.filename.rsplit('.', 1)[0]}.csv"
    save_path = os.path.join(data_dir, unique_name)
    df.to_csv(save_path, index=False)
    logger.info(f"File saved to {save_path}")

    return UploadResult(rows_loaded=df.shape[0], rows_failed=0)
