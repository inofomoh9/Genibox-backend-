from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
import zipfile
import uuid

app = FastAPI()

# CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_app(app_name: str = Form(...), description: str = Form(...), pages: str = Form(...)):
    folder_id = str(uuid.uuid4())
    folder_path = f"./apps/{folder_id}"
    os.makedirs(folder_path, exist_ok=True)

    pages_list = pages.split(',')

    # Create files for each page
    for page in pages_list:
        page = page.strip()
        with open(f"{folder_path}/{page}.html", 'w') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
  <title>{page} - {app_name}</title>
</head>
<body>
  <h1>Welcome to {page}</h1>
  <p>{description}</p>
</body>
</html>
""")

    # Zip it
    zip_name = f"{folder_id}.zip"
    zip_path = f"./apps/{zip_name}"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    # Cleanup folder
    shutil.rmtree(folder_path)

    return JSONResponse({"zip_file": zip_name})


@app.get("/download/{zip_file}")
def download(zip_file: str):
    file_path = f"./apps/{zip_file}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=zip_file)
    return JSONResponse({"error": "File not found"})
