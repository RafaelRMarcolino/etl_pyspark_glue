from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from pyspark.sql.functions import date_format, current_date
from awsglue.utils import getResolvedOptions
import sys

# Pega os argumentos passados no Glue Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
input_path = args['input_path']
output_path = args['output_path']

# Inicializa a SparkSession
spark = SparkSession.builder.appName("IngestaoClientesCSVtoParquet").getOrCreate()

# Define o schema explicitamente
schema = StructType([
    StructField("cliente_id", IntegerType(), True),
    StructField("nome", StringType(), True),
    StructField("data_nascimento", StringType(), True)
])

df = spark.read.csv(input_path, header=True, schema=schema)
df = df.withColumn("data_carga", date_format(current_date(), "yyyy-MM-dd"))
df.printSchema()


df.write.mode("overwrite").partitionBy("data_carga").parquet(output_path)

spark.stop()
