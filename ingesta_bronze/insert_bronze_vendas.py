from pyspark.sql import SparkSession
from pyspark.sql.functions import substring, col, date_format, current_date
from pyspark.sql.types import IntegerType, DecimalType, StringType
from awsglue.utils import getResolvedOptions
import sys

# Pega os argumentos passados no Glue Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
input_path = args['input_path']
output_path = args['output_path']


spark = SparkSession.builder.appName("IngestaoVendasPosicionalToParquet").getOrCreate()

# Lê o arquivo como texto bruto
df_raw = spark.read.text(input_path)

# Extrai os campos com substring e converte para os tipos corretos
df = df_raw.select(
    substring("value", 1, 5).cast(IntegerType()).alias("venda_id"),
    substring("value", 6, 5).cast(IntegerType()).alias("cliente_id"),
    substring("value", 11, 5).cast(IntegerType()).alias("produto_id"),
    (substring("value", 16, 8).cast(DecimalType(10, 2)) / 100).alias("valor"),
    substring("value", 24, 8).alias("data_venda")
)


df = df.withColumn("data_carga", date_format(current_date(), "yyyy-MM-dd"))
df.printSchema()
df.write.mode("overwrite").partitionBy("data_carga").parquet(output_path)

spark.stop()
