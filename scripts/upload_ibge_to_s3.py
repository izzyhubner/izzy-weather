
from pathlib import Path

import boto3

BUCKET_NAME = "izzy-weather"
S3_KEY = "raw/ibge/RELATORIO_DTB_BRASIL_MUNICIPIO.xls"

LOCAL_DIR = Path("data/raw/ibge")

matches = list(LOCAL_DIR.glob("RELATORIO_DTB_BRASIL_MUNICIPIO.xls*"))

if len(matches) != 1:
    raise FileNotFoundError(
        f"Expected one matching IBGE file in {LOCAL_DIR.resolve()}, "
        f"but found {len(matches)}: {matches}"
    )

local_file = matches[0]

s3 = boto3.client("s3")

s3.upload_file(
    str(local_file),
    BUCKET_NAME,
    S3_KEY
)

print("IBGE file uploaded successfully!")
print(f"Local file: {local_file}")
print(f"S3 location: s3://{BUCKET_NAME}/{S3_KEY}")
