import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, status, HTTPException
from fastapi import Response

from app.database import File as FileDB
from app.database import Folder as FolderDB
from app.extensions.s3 import S3Bucket
from app.schemas import FolderBaseSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create(
        name: str,
):
    folder_uuid = str(uuid.uuid4())
    try:
        FolderDB.insert_one(
            FolderBaseSchema(
                name=name,
                user_uuid="",
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


@router.get("/all", status_code=status.HTTP_200_OK)
async def all_folders():
    try:
        folders = []
        for f in FolderDB.find({}):
            folders.append(
                FolderBaseSchema(
                    name=f.get("name", ""),
                    user_uuid=f.get("user_uuid", ""),
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


@router.delete("/delete/{folder_uuid}", status_code=status.HTTP_200_OK)
async def delete(folder_uuid: str):
    try:
        keys_to_delete = []
        for file in FileDB.find({"folder_uuid": folder_uuid}):
            keys_to_delete.append(file.get("key", ""))

        for key in keys_to_delete:
            s3 = S3Bucket()
            s3.delete_file(key)
            FileDB.delete_one({"key": key})

        FolderDB.delete_one({"folder_uuid": folder_uuid})
    except Exception as e:
        logger.error(f"Error on delete folder {folder_uuid}, error: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error on deleting folder"
        )

    return {"message": f"Folder {folder_uuid} deleted with success"}
