from pyspark.sql import SparkSession
from pyspark.sql.functions import when, lit, col, to_timestamp, datediff, current_timestamp, row_number
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("voucher_selection").getOrCreate()

# Reading data from input folder. Every new file with vouchers can be deposited here.
# Partitions can be implemented in the future
vouchers_data_df = spark.read.load('../data/input')

# Starting with transformations discovered in Exploratory Data Analysis
# 1. Filtering data for Peru vouchers
vouchers_peru_df = vouchers_data_df.where("country_code='Peru'")

# 2. Drop rows with null values
vouchers_notnull_df = vouchers_peru_df.dropna()

# 3. Drop duplicates
vouchers_dedup_df = vouchers_notnull_df.drop_duplicates()

# 4. Drop rows with total_orders column with empty values
vouchers_total_orders_without_empty = vouchers_dedup_df.where("total_orders != ''")

# 5. Cast total_orders column to int type
# 6. Cast last_order_ts and timestamp columns to datetime64[ns, UTC] type
vouchers_trusted_df = vouchers_total_orders_without_empty.select(
    to_timestamp(col('timestamp')).alias('timestamp'),
    col('country_code'),
    col('first_order_ts'),
    to_timestamp(col('last_order_ts')).alias('last_order_ts'),
    col('total_orders').cast(IntegerType()).alias('total_orders'),
    col('voucher_amount')
)

# Starting with segments creation
# Final outcome will be 2 different datasets, that will be stored as 2 different files. One for frequent_segment and
# another one for recency_segment. Each dataframe will store the segment and the most used (the mode) voucher amount.
# The dataframe will be something like this:
# segment | most_used_voucher_amount
# --------|--------------------------
# 0-4     | 4400
# 5-13    | 2640

# Adding segment to each transaction
vouchers_segments = vouchers_trusted_df.withColumn(
    'frequent_segment',
    when(
        col('total_orders').between(0, 4), lit('0-4')
    ).when(
        col('total_orders').between(5, 13), lit('5-13')
    ).when(
        col('total_orders').between(14, 37), lit('14-37')
    ).otherwise('undefined')
    # undefined segment added, just in case business rule changes in the future, can easily being updated
).withColumn(
    'order_days_diff',
    # Function datediff should be performed over current date, to get recency segment.
    # This creates the need to schedule this pipeline at lest once a day
    datediff(current_timestamp(), col('last_order_ts'))
).withColumn(
    'recency_segment',
    when(
        col('order_days_diff').between(30, 60), lit('30-60')
    ).when(
        col('order_days_diff').between(61, 90), lit('61-90')
    ).when(
        col('order_days_diff').between(91, 120), lit('61-90')
    ).when(
        col('order_days_diff').between(121, 180), lit('61-90')
    ).when(
        col('order_days_diff') > 180, lit('180+')
    ).otherwise('undefined')
    # undefined segment added, just in case business rule changes in the future, can easily being updated
    # Saving dataframe in cache, as it will be called twice, to build segments
).cache()


# Splitting dataframe into 2 different df. Each df will be stored as an individual dataset

# Creating method to built final dataset for each segment type

def build_segment_dataset(vouchers_df, segment_name):
    segment_df = vouchers_df.groupby(
        col(segment_name), col('voucher_amount')
    ).count().withColumn(
        'rown',
        row_number().over(Window.partitionBy(col(segment_name)).orderBy(col('count').desc()))
    ).select(
        col(segment_name).alias('segment_name'),
        col('voucher_amount')
    ).where(f"rown = 1 and {segment_name} != 'undefined'")

    return segment_df


# Creating dataset for each segment
frequent_segment_df = build_segment_dataset(vouchers_segments, 'frequent_segment')
recency_segment_df = build_segment_dataset(vouchers_segments, 'recency_segment')


# Function to save the final result into separate files
def write_segment_df(segment_df, segment_name):
    segment_df\
        .write\
        .format('parquet')\
        .mode('overwrite')\
        .save(f'../data/output/{segment_name}')


# Writing both datasets
write_segment_df(frequent_segment_df, 'frequent_segment')
write_segment_df(recency_segment_df, 'recency_segment')

#print(spark.read.parquet('../data/output/recency_segment').where("segment_name = '180+'").first()['voucher_amount'])

# print(frequent_segment_df.count())
# frequent_segment_df.printSchema()
# frequent_segment_df.show(truncate=False)
#
# print(recency_segment_df.count())
# recency_segment_df.printSchema()
# recency_segment_df.show(truncate=False)
