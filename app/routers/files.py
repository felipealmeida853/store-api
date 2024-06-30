import json
import logging
import uuid
from datetime import datetime

import jwt
from fastapi import APIRouter, status, HTTPException, UploadFile, Depends
from fastapi import Response, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from app.config import settings
from app.database import File as FileDB
from app.extensions.s3 import S3Bucket
from app.routers.user import jwt_required
from app.schemas import FileBaseSchema
from app.utils import remove_file

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{folder_uuid}/save", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(jwt_required)])
async def save(
        folder_uuid: str,
        file: UploadFile,
        request: Request
):
    try:
        key = f"{str(uuid.uuid4())}_{file.filename}"
        s3 = S3Bucket()
        s3.save_file(file.file, key)
    except Exception as e:
        logger.error(f"Error on upload file {key}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on downloading file"
        )

    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")
        FileDB.insert_one(
            FileBaseSchema(
                name=file.filename,
                user=username,
                folder_uuid=folder_uuid,
                key=key,
                created_at=datetime.utcnow(),
                bucket=settings.BUCKET_NAME,
            ).dict()
        )
    except Exception as error:
        logger.error(f"Error on insert file on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )
    return {"message": f"File saved with success {key}"}


@router.get("/all", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def all_files(request: Request):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")
        files = []
        for f in FileDB.find({"user": username}):
            files.append(
                FileBaseSchema(
                    name=f.get("name", ""),
                    user=f.get("user", ""),
                    folder_uuid=f.get("folder_uuid", ""),
                    key=f.get("key", ""),
                    created_at=str(f.get("created_at", "")),
                    bucket=f.get("bucket", ""),
                ).dict()
            )

    except Exception as error:
        logger.error(f"Error on get files on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting file"
        )

    return Response(content=json.dumps(files, indent=4, sort_keys=True, default=str), media_type="application/json")


@router.get("/folder/{folder_uuid}/all", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def all_files_by_folder(
        folder_uuid: str,
        request: Request,
):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")
        files = []
        for f in FileDB.find({"folder_uuid": folder_uuid, "user": username}):
            files.append(
                FileBaseSchema(
                    name=f.get("name", ""),
                    user=f.get("user", ""),
                    folder_uuid=f.get("folder_uuid", ""),
                    key=f.get("key", ""),
                    created_at=str(f.get("created_at", "")),
                    bucket=f.get("bucket", ""),
                ).dict()
            )

    except Exception as error:
        logger.error(f"Error on get files on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting file"
        )
    return Response(content=json.dumps(files, indent=4, sort_keys=True, default=str), media_type="application/json")


@router.get("/download/{key}", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def download(
        key: str,
        background_tasks: BackgroundTasks,
        request: Request,
):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")

        file = FileDB.find_one({"key": key, "user": username})
        if file:
            s3 = S3Bucket()
            path = s3.get_file(file.key)
        else:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not Found"
            )
    except Exception as e:
        logger.error(f"Error downloading file {key}, Error: {e}")
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

    background_tasks.add_task(remove_file, path)
    return FileResponse(path)


@router.delete("/delete/{key}", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def delete(key: str, request: Request):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")

        file = FileDB.find_one({"key": key, "user": username})
        if file:
            s3 = S3Bucket()
            s3.delete_file(key)
            FileDB.delete_one({"key": key})
    except Exception as e:
        logger.error(f"Error on download file {key}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on downloading file"
        )

    return {"message": f"File {key} deleted with success"}
