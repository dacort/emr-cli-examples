from pyspark.sql import SparkSession
from jobs.job1 import Job1

if __name__ == "__main__":
    sc = SparkSession.builder.getOrCreate()
    j = Job1(sc)
    # Prints out the max temp from Seattle in 2023
    print(j.max_temp(2023, 72793524234))
