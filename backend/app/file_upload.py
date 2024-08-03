from uuid import uuid4
import base64
import asyncio
from app.firebase_startup import firebase_storage


class FileUploadService:
    async def upload(self, file, file_type):
        filename = f"{uuid4()}.{file_type}"
        if "," in file:
            file = file.split(",")[1]
        encoded_file = base64.b64decode(file)
        await asyncio.to_thread(firebase_storage.child(filename).put, encoded_file)
        file_url = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
        return file_url
