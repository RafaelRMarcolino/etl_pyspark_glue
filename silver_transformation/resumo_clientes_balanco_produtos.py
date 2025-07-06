from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, round, col, date_format, current_date
from awsglue.utils import getResolvedOptions
import sys
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




# Pega os argumentos passados no Glue Job
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'resumo_clientes_output_path',
    'balanco_produtos_output_path'
])

resumo_output_path = args['resumo_clientes_output_path'].rstrip('/')  # remove / final se houver
balanco_output_path = args['balanco_produtos_output_path'].rstrip('/')

spark = SparkSession.builder.appName("PipelineClientesProdutos").getOrCreate()

bucket = "bucket-clientes-vendas-py"
clientes_prefix = "bronze/clientes/"
vendas_prefix = "bronze/vendas/"

# Recupera a última partição
latest_clientes = get_latest_partition(bucket, clientes_prefix)
latest_vendas = get_latest_partition(bucket, vendas_prefix)

if not latest_clientes or not latest_vendas:
    raise ValueError(
        f"[ERRO] Não foi possível recuperar a última partição:"
        f" clientes=({latest_clientes}), vendas=({latest_vendas})"
    )

clientes_input_path = f"s3://{bucket}/{clientes_prefix}data_carga={latest_clientes}/"
vendas_input_path = f"s3://{bucket}/{vendas_prefix}data_carga={latest_vendas}/"

print(f"[INFO] Lendo clientes de: {clientes_input_path}")
print(f"[INFO] Lendo vendas de: {vendas_input_path}")

# Leitura
df_clientes = spark.read.parquet(clientes_input_path)
df_vendas = spark.read.parquet(vendas_input_path)

# Gera o valor da partição (data_carga)
data_carga_value = date_format(current_date(), "yyyy-MM-dd").cast("string")

# Resumo por cliente
df_resumo = (
    df_clientes.join(df_vendas, "cliente_id", "inner")
    .groupBy("cliente_id", "nome")
    .agg(
        sum("valor").alias("total_vendas"),
        count("venda_id").alias("quantidade_vendas")
    )
    .withColumn("ticket_medio", round(col("total_vendas") / col("quantidade_vendas"), 2))
    .withColumn("data_carga", date_format(current_date(), "yyyy-MM-dd"))
)

print("[INFO] Schema do DataFrame resumo_clientes:")
df_resumo.printSchema()

df_resumo.write \
    .mode("overwrite") \
    .partitionBy("data_carga") \
    .parquet(resumo_output_path)

print(f"[INFO] Dados de resumo_clientes salvos em {resumo_output_path}")

# Balanço por produto
df_balanco = (
    df_vendas.groupBy("produto_id")
    .agg(
        sum("valor").alias("total_vendas_produto"),
        count("venda_id").alias("quantidade_vendas_produto")
    )
    .withColumn("ticket_medio_produto", round(col("total_vendas_produto") / col("quantidade_vendas_produto"), 2))
    .withColumn("data_carga", date_format(current_date(), "yyyy-MM-dd"))
)

print("[INFO] Schema do DataFrame balanco_produtos:")
df_balanco.printSchema()

df_balanco.write \
    .mode("overwrite") \
    .partitionBy("data_carga") \
    .parquet(balanco_output_path)

print(f"[INFO] Dados de balanco_produtos salvos em {balanco_output_path}")

spark.stop()
