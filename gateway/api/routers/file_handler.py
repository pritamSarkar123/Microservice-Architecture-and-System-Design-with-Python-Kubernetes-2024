import gridfs
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse

from .. import utils
from ..auth import validateToken
from ..db import client
from bson.objectid import ObjectId
from io import BytesIO

router = APIRouter(
    prefix="/api/v1/file",
    tags=["upload-router"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def create_upload(request: Request, file: UploadFile = File(...)):
    token_validation_dict = await validateToken(request)
    if "valid" not in token_validation_dict or not token_validation_dict["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=token_validation_dict["detail"],
        )

    database = client["videos"]
    fs = gridfs.GridFS(database)

    # {"valid": True, "admin": adimin_user, "email": user_email}
    # if not token_validation_dict["admin"]:
    content = await file.read()
    err = await utils.upload(content, fs, metadata=token_validation_dict)
    if err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )

    return {"status": "Success"}


@router.get("/download")
async def download(request: Request,fid: str=""):  # TODO
    token_validation_dict = await validateToken(request)
    if "valid" not in token_validation_dict or not token_validation_dict["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=token_validation_dict["detail"],
        )

    # {"valid": True, "admin": adimin_user, "email": user_email}
    # if not token_validation_dict["admin"]:
    if not fid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request file id not found")
    
    try:    
        out = None
        file_id = None
        database = client["mp3s"]
        fs = gridfs.GridFS(database)
        try:
            file_id = ObjectId(fid)
        except Exception as e:
            raise Exception("Bad Request invalid file id")
        try:
            out = fs.get(file_id)
            file_data = BytesIO(out.read())
            file_data.seek(0)
            fs.delete(file_id)
            print(f'Deleted file with id {str(file_id)}')
        except Exception:
            raise Exception(f"File not found id {str(file_id)}")
        return StreamingResponse(
            file_data,
            media_type="application/octet-stream",
             headers={"Content-Disposition": f"attachment; filename={fid}.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    