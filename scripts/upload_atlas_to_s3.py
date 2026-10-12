
from pathlib import Path

import boto3

BUCKET_NAME = "izzy-weather"
S3_KEY = (
    "raw/atlasdigital/"
    "BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv"
)

LOCAL_FILE = Path(
    "data/raw/atlasdigital/"
    "BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv"
)

if not LOCAL_FILE.exists():
    raise FileNotFoundError(f"File not found: {LOCAL_FILE.resolve()}")

s3 = boto3.client("s3")

s3.upload_file(
    str(LOCAL_FILE),
    BUCKET_NAME,
    S3_KEY
)

print("Upload successful!")
print(f"Local file: {LOCAL_FILE}")
print(f"S3 location: s3://{BUCKET_NAME}/{S3_KEY}")
