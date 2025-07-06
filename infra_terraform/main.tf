resource "aws_s3_object" "athena_results_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "athena-results/"
}

resource "aws_s3_object" "bronze_clientes_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "bronze/clientes/"
}

resource "aws_s3_object" "bronze_vendas_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "bronze/vendas/"
}

resource "aws_s3_object" "temp_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "temp/"
}

resource "aws_s3_object" "resumo_clientes_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "silver/resumo_clientes/"
}

resource "aws_s3_object" "balanco_produtos_folder" {
  bucket = "bucket-clientes-vendas-py"
  key    = "silver/balanco_produtos/"
}

resource "aws_glue_catalog_database" "bronze_db" {
  name = "bronze"
}

resource "aws_glue_catalog_database" "silver_db" {
  name = "silver"
}

resource "aws_glue_catalog_table" "clientes_bronze" {
  name          = "clientes_bronze"
  database_name = aws_glue_catalog_database.bronze_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
    "EXTERNAL"       = "TRUE"
  }

  storage_descriptor {
    location      = "s3://bucket-clientes-vendas-py/bronze/clientes/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "parquet-serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "nome"
      type = "string"
    }
    columns {
      name = "idade"
      type = "int"
    }
    columns {
      name = "cidade"
      type = "string"
    }
  }

  partition_keys {
    name = "data_carga"
    type = "string"
  }
}

resource "aws_glue_catalog_table" "vendas_bronze" {
  name          = "vendas_bronze"
  database_name = aws_glue_catalog_database.bronze_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
    "EXTERNAL"       = "TRUE"
  }

  storage_descriptor {
    location      = "s3://bucket-clientes-vendas-py/bronze/vendas/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "parquet-serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "venda_id"
      type = "int"
    }
    columns {
      name = "cliente_id"
      type = "int"
    }
    columns {
      name = "produto_id"
      type = "int"
    }
    columns {
      name = "valor"
      type = "decimal(10,2)"
    }
    columns {
      name = "data_venda"
      type = "string"
    }
  }

  partition_keys {
    name = "data_carga"
    type = "string"
  }
}

resource "aws_glue_catalog_table" "resumo_clientes" {
  name          = "resumo_clientes"
  database_name = aws_glue_catalog_database.silver_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
    "EXTERNAL"       = "TRUE"
  }

  storage_descriptor {
    location      = "s3://bucket-clientes-vendas-py/silver/resumo_clientes/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "parquet-serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "cliente_id"
      type = "int"
    }
    columns {
      name = "nome"
      type = "string"
    }
    columns {
      name = "total_vendas"
      type = "decimal(14,2)"
    }
    columns {
      name = "quantidade_vendas"
      type = "bigint"
    }
    columns {
      name = "ticket_medio"
      type = "decimal(14,2)"
    }
  }

  partition_keys {
    name = "data_carga"
    type = "string"
  }
}

resource "aws_glue_catalog_table" "balanco_produtos" {
  name          = "balanco_produtos"
  database_name = aws_glue_catalog_database.silver_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
    "EXTERNAL"       = "TRUE"
  }

  storage_descriptor {
    location      = "s3://bucket-clientes-vendas-py/silver/balanco_produtos/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "parquet-serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "produto_id"
      type = "int"
    }
    columns {
      name = "total_vendas_produto"
      type = "decimal(14,2)"
    }
    columns {
      name = "quantidade_vendas_produto"
      type = "bigint"
    }
    columns {
      name = "ticket_medio_produto"
      type = "decimal(14,2)"
    }
  }

  partition_keys {
    name = "data_carga"
    type = "string"
  }
}

resource "aws_glue_job" "ingesta_bronze_clientes" {
  name     = "ingesta_bronze_clientes"
  role_arn = "arn:aws:iam::609803702667:role/glue_service_role"

  command {
    name            = "glueetl"
    script_location = "s3://bucket-clientes-vendas-py/scripts/ingesta_bronze/bronze_clientes.py"
    python_version  = "3"
  }

  glue_version      = "3.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  max_retries       = 0

  default_arguments = {
    "--TempDir"      = "s3://bucket-clientes-vendas-py/temp/"
    "--job-language" = "python"
    "--input_path"   = "s3://bucket-clientes-vendas-py/data/clientes.csv"
    "--output_path"  = "s3://bucket-clientes-vendas-py/bronze/clientes/"
  }
}

resource "aws_glue_job" "ingesta_bronze_vendas" {
  name     = "ingesta_bronze_vendas"
  role_arn = "arn:aws:iam::609803702667:role/glue_service_role"

  command {
    name            = "glueetl"
    script_location = "s3://bucket-clientes-vendas-py/scripts/ingesta_bronze/bronze_vendas.py"
    python_version  = "3"
  }

  glue_version      = "3.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  max_retries       = 0

  default_arguments = {
    "--TempDir"      = "s3://bucket-clientes-vendas-py/temp/"
    "--job-language" = "python"
    "--input_path"   = "s3://bucket-clientes-vendas-py/data/vendas.txt"
    "--output_path"  = "s3://bucket-clientes-vendas-py/bronze/vendas/"
  }
}


resource "aws_glue_job" "pipeline_clientes_produtos" {
  name     = "pipeline_clientes_produtos"
  role_arn = "arn:aws:iam::609803702667:role/glue_service_role"

  command {
    name            = "glueetl"
    script_location = "s3://bucket-clientes-vendas-py/scripts/transformation/resumo_clientes_balanco_produtos.py"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"                     = "s3://bucket-clientes-vendas-py/temp/"
    "--job-language"                 = "python"
    "--resumo_clientes_output_path"  = "s3://bucket-clientes-vendas-py/silver/resumo_clientes/"
    "--balanco_produtos_output_path" = "s3://bucket-clientes-vendas-py/silver/balanco_produtos/"
  }

  max_retries = 0
  glue_version = "3.0"
  number_of_workers = 2
  worker_type = "G.1X"
}
