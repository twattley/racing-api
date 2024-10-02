from api_helpers.s3_client import S3Client, S3Connection

from src.config import Config


def get_s3_client():
    config = Config()
    return S3Client(
        connection=S3Connection(
            access_key_id=config.do_spaces_access_key,
            secret_access_key=config.do_spaces_secret_access_key,
            region_name=config.do_spaces_region_name,
            endpoint_url=config.do_spaces_endpoint_url,
            bucket_name=config.do_spaces_bucket_name,
        )
    )
