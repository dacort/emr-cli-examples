from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Damon").getOrCreate()
print("Hello, world!")
