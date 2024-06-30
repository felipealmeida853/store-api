import json
import logging
import uuid
from datetime import datetime

import jwt
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi import Response, Request

from app.config import settings
from app.database import File as FileDB
from app.database import Folder as FolderDB
from app.extensions.s3 import S3Bucket
from app.routers.user import jwt_required
from app.schemas import FolderBaseSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", status_code=status.HTTP_201_CREATED, dependencies=[Depends(jwt_required)])
async def create(
        name: str,
        request: Request,
):
    token_bearer = request.headers.get('Authorization')
    username = ""
    if token_bearer:
        token_split = token_bearer.split(" ")
        token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username = token_data.get("sub")
    folder_uuid = str(uuid.uuid4())
    try:
        FolderDB.insert_one(
            FolderBaseSchema(
                name=name,
                user=username,
                folder_uuid=folder_uuid,
                created_at=datetime.utcnow(),
            ).dict()
        )
    except Exception as error:
        logger.error(f"Error on insert folder on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating folder"
        )
    return {"message": f"Folder created with success {folder_uuid}"}


@router.get("/all", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def all_folders(request: Request):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")
        folders = []
        for f in FolderDB.find({"user": username}):
            folders.append(
                FolderBaseSchema(
                    name=f.get("name", ""),
                    user=f.get("user", ""),
                    key=f.get("key", ""),
                    created_at=str(f.get("created_at", "")),
                    bucket=f.get("bucket", ""),
                ).dict()
            )

    except Exception as error:
        logger.error(f"Error on get folders on DB {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting folder"
        )
    return Response(content=json.dumps(folders, indent=4, sort_keys=True, default=str), media_type="application/json")


@router.delete("/delete/{folder_uuid}", status_code=status.HTTP_200_OK, dependencies=[Depends(jwt_required)])
async def delete(folder_uuid: str, request: Request):
    try:
        token_bearer = request.headers.get('Authorization')
        username = ""
        if token_bearer:
            token_split = token_bearer.split(" ")
            token_data = jwt.decode(token_split[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            username = token_data.get("sub")
        keys_to_delete = []
        for file in FileDB.find({"folder_uuid": folder_uuid, "user": username}):
            keys_to_delete.append(file.get("key", ""))

        for key in keys_to_delete:
            s3 = S3Bucket()
            s3.delete_file(key)
            FileDB.delete_one({"key": key})

        FolderDB.delete_one({"folder_uuid": folder_uuid, "user": username})
    except Exception as e:
        logger.error(f"Error on delete folder {folder_uuid}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on deleting folder"
        )

    return {"message": f"Folder {folder_uuid} deleted with success"}
