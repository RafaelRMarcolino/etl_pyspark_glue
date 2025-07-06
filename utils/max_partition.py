import boto3
import re

def get_latest_partition(bucket: str, prefix: str) -> str:
    """
    Encontra a última partição no S3 que bate com o padrão:
      {prefix}data_carga=YYYY-MM-DD/
    Retorna somente a string YYYY-MM-DD.
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/")

    partitions = []
    for page in pages:
        for cp in page.get("CommonPrefixes", []):
            folder = cp["Prefix"]                # ex: "bronze/clientes/data_carga=2025-07-05/"
            m = re.search(r"data_carga=(\d{4}-\d{2}-\d{2})", folder)
            if m:
                partitions.append(m.group(1))

    if not partitions:
        raise RuntimeError(f"Nenhuma partição encontrada em s3://{bucket}/{prefix}")

    return sorted(partitions)[-1]
