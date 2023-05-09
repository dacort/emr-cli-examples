from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("SparkSQL")
    # .config(
    #     "hive.metastore.client.factory.class",
    #     "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory",
    # )
    # This config can a;sp be specified with the emr-cli using the following option:
    # --spark-submit-opts "--conf spark.hadoop.hive.metastore.client.factory.class=com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
    .enableHiveSupport()
    .getOrCreate()
)

# We can query tables with SparkSQL
spark.sql("SHOW TABLES").show()

# Or we can also them with native Spark code
print(spark.catalog.listTables())