from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends

from src.database.core import DbSession, get_db
from src.uploads import service
from src.uploads.service import process

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"]
)


@router.post(
    "/excel",
    summary="Загрузить Excel-файл с данными",
    status_code=status.HTTP_201_CREATED,
)
def upload_excel(
    file: UploadFile = File(..., description="Excel-файл (.xlsx или .xls)"),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неподдерживаемый формат, загрузите .xlsx или .xls"
        )
    try:
        result = service.process(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка обработки файла: {e}"
        )

    return {
        "message": "Файл успешно обработан и сохранён в CSV",
        "rows_loaded": result.rows_loaded,
        "rows_error": result.rows_failed
    }
