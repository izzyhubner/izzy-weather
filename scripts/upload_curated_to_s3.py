
from pathlib import Path

import boto3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOCAL_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "atlasdigital"
    / "atlas_disasters.parquet"
)

BUCKET_NAME = "izzy-weather"
S3_KEY = "curated/atlasdigital/atlas_disasters.parquet"


def main():
    if not LOCAL_PATH.exists():
        raise FileNotFoundError(f"File not found: {LOCAL_PATH}")

    s3 = boto3.client("s3")

    s3.upload_file(
        str(LOCAL_PATH),
        BUCKET_NAME,
        S3_KEY,
    )

    print(f"Uploaded to s3://{BUCKET_NAME}/{S3_KEY}")


if __name__ == "__main__":
    main()
