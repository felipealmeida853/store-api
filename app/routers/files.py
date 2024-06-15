import json
import uuid
from datetime import datetime

from fastapi import APIRouter, status, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import File as FileDB
from app.schemas import FileBaseSchema
from app.extensions.s3 import S3Bucket
from starlette.background import BackgroundTasks

from app.utils import remove_file

router = APIRouter()


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save(
    file: UploadFile,
):
    try:
        key = f"{str(uuid.uuid4())}_{file.filename}"
        s3 = S3Bucket()
        s3.save_file(file.file, key)
    except Exception as e:
        print(f"Error on upload file {key}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on downloading file"
        )

    try:
        FileDB.insert_one(
            FileBaseSchema(
                name=file.filename,
                user_uuid="",
                key=key,
                created_at=datetime.utcnow(),
                bucket=settings.BUCKET_NAME,
            ).dict()
        )
    except Exception as error:
        print(f"Error on insert file on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )
    return {"message": f"File saved with success {key}"}


@router.get("/all", status_code=status.HTTP_200_OK)
async def all_files():
    try:
        files = []
        for f in FileDB.find({}):
            if not f.get("deleted", False):
                files.append(
                    FileBaseSchema(
                        name=f.get("name", ""),
                        user_uuid=f.get("user_uuid", ""),
                        key=f.get("key", ""),
                        created_at=str(f.get("created_at", "")),
                        bucket=f.get("bucket", ""),
                    ).dict()
                )

    except Exception as error:
        print(f"Error on get files on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting file"
        )
    return JSONResponse(
        json.dumps(files, indent=4, sort_keys=True, default=str)
    )


@router.get("/download/{key}", status_code=status.HTTP_200_OK)
async def download(
    key: str,
    background_tasks: BackgroundTasks
):
    try:
        s3 = S3Bucket()
        path = s3.get_file(key)
    except Exception as e:
        print(f"Error: {e}")
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

    background_tasks.add_task(remove_file, path)
    return FileResponse(path)


@router.delete("/delete/{key}", status_code=status.HTTP_200_OK)
async def delete(key: str):
    try:
        s3 = S3Bucket()
        s3.delete_file(key)
        FileDB.delete_one({"key": key})
    except Exception as e:
        print(f"Error on download file {key}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on downloading file"
        )

    return {"message": f"File {key} deleted with success"}
