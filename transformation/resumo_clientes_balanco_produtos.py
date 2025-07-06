from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, round, col
from awsglue.utils import getResolvedOptions
import sys

# Pega os argumentos do Glue Job
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'clientes_input_path',
    'vendas_input_path',
    'resumo_clientes_output_path',
    'balanco_produtos_output_path'
])

clientes_input_path = args['clientes_input_path']
vendas_input_path = args['vendas_input_path']
resumo_clientes_output_path = args['resumo_clientes_output_path']
balanco_produtos_output_path = args['balanco_produtos_output_path']


spark = SparkSession.builder.appName("pipeline_clientes_produtos").getOrCreate()


df_clientes = spark.read.parquet(clientes_input_path)
df_vendas = spark.read.parquet(vendas_input_path)



df_resumo_clientes = (
    df_clientes.join(df_vendas, "cliente_id", "inner")
    .groupBy("cliente_id", "nome")
    .agg(
        sum("valor").alias("total_vendas"),
        count("venda_id").alias("quantidade_vendas")
    )
    .withColumn(
        "ticket_medio",
        round(col("total_vendas") / col("quantidade_vendas"), 2)
    )
    .orderBy("cliente_id")
)


df_resumo_clientes.write.mode("overwrite").parquet(resumo_clientes_output_path)


df_balanco_produtos = (
    df_vendas.groupBy("produto_id")
    .agg(
        sum("valor").alias("total_vendas_produto"),
        count("venda_id").alias("quantidade_vendas_produto")
    )
    .withColumn(
        "ticket_medio_produto",
        round(col("total_vendas_produto") / col("quantidade_vendas_produto"), 2)
    )
)


df_balanco_produtos.write.mode("overwrite").parquet(balanco_produtos_output_path)

spark.stop()
