from pyspark.sql import SparkSession
from pyspark.sql import functions as F


class Job1:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def max_temp(self, year: int, station_id: int) -> float:
        data_file = f"s3://noaa-gsod-pds/{year}/{station_id}.csv"
        df = self.spark.read.csv(data_file, header=True, inferSchema=True)
        top_temp = df.select("temp").orderBy(F.desc("temp")).limit(1).first()
        return top_temp["temp"]
