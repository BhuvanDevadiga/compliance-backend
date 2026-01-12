import boto3
import uuid
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.database import get_db
from app.model import Document
from app.config import settings
from app.auth import get_current_user
from pydantic import BaseModel  

class DocumentUploadRequest(BaseModel):
    user_id: int

class DocumentUploadResponse(BaseModel):
    user_id: int

router = APIRouter(prefix="/documents")

s3 = boto3.client("s3", region_name=settings.AWS_REGION)

@router.post("/upload")
async def upload_document(
    request: DocumentUploadRequest, 
    file: UploadFile, 
    db=Depends(get_db),
    current_user: str = Depends(get_current_user),  
):
    try:
        key = f"{request.user_id}/{uuid.uuid4()}-{file.filename}"

        
        s3.upload_fileobj(
            file.file,
            settings.AWS_BUCKET,
            key,
            ExtraArgs={"ACL": "private"}
        )

        
        doc = Document(
            user_id=request.user_id,
            type="unknown",
            s3_key=key,
            extracted_data={}
        )
        db.add(doc)
        db.commit()

        return {"message": "Uploaded securely"}
    except boto3.exceptions.Boto3Error as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")