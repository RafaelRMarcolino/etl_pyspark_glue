
# ETL_PYSPARK_GLUE

Projeto de pipeline de dados utilizando **PySpark**, **AWS Glue**, **Amazon S3** e **Terraform** para ingestão e transformação de dados em um data lake na AWS.

## 🚀 Tecnologias

- **Python 3.x**
- **PySpark**
- **AWS S3**
- **AWS Glue**
- **Terraform**

## 📂 Estrutura do Projeto

```
ETL_PYSPARK_GLUE/
├── data/
│   ├── clientes.csv
│   └── vendas.txt
├── infra_terraform/
│   ├── main.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── variables.tf
│   └── ...
├── ingesta_bronze/
│   ├── insert_bronze_clientes.py
│   └── insert_bronze_vendas.py
├── silver_transformation/
│   └── resumo_clientes_balanco_produtos.py
├── utils/
│   └── max_partition.py
├── requirements.txt
└── README.md
```

## 🔑 Pré-requisitos

- AWS CLI configurado com acesso à conta AWS
- Terraform instalado
- Python 3.x com PySpark instalado localmente (para testes, se necessário)
- Permissões no AWS S3, Glue e Athena

## ⚙️ Configuração inicial

### Configurar credenciais AWS

```bash
aws configure
```

Informe:
- Access Key ID
- Secret Access Key
- Região (ex: `us-east-1`)
- Formato de saída (opcional: `json`)

### Provisionar infraestrutura com Terraform

No diretório `infra_terraform/`:

```bash
terraform init
terraform plan
terraform apply
```

## 📤 Upload dos arquivos para o S3

### Dados

```bash
aws s3 cp data/clientes.csv s3://bucket-clientes-vendas-py/data/clientes.csv
aws s3 cp data/vendas.txt s3://bucket-clientes-vendas-py/data/vendas.txt
```

### Scripts

```bash
aws s3 cp ingesta_bronze/insert_bronze_clientes.py s3://bucket-clientes-vendas-py/scripts/ingesta_bronze/bronze_clientes.py
aws s3 cp ingesta_bronze/insert_bronze_vendas.py s3://bucket-clientes-vendas-py/scripts/ingesta_bronze/bronze_vendas.py
aws s3 cp silver_transformation/resumo_clientes_balanco_produtos.py s3://bucket-clientes-vendas-py/scripts/transformation/resumo_clientes_balanco_produtos.py
```

## 🛠️ Execução dos Glue Jobs

1. Acesse o AWS Glue → ETL Jobs
2. Execute os jobs:
   - `ingesta_bronze_clientes`: cria a tabela `bronze.clientes_bronze`
   - `ingesta_bronze_vendas`: cria a tabela `bronze.vendas_bronze`
   - `pipeline_clientes_produtos`: gera `silver.resumo_clientes` e `silver.balanco_produtos`

Logs disponíveis no **CloudWatch Logs**.

## 🏗️ Atualizar metadados no Glue Catalog

```sql
MSCK REPAIR TABLE bronze.clientes_bronze;
MSCK REPAIR TABLE bronze.vendas_bronze;
MSCK REPAIR TABLE silver.resumo_clientes;
MSCK REPAIR TABLE silver.balanco_produtos;
```

## 📦 Dependências

Exemplo do `requirements.txt`:

```
boto3
pyspark
```

## 📌 Observações

- Substitua `bucket-clientes-vendas-py` pelo seu bucket real.
- Adapte os nomes no Glue/Athena conforme o Data Catalog.
