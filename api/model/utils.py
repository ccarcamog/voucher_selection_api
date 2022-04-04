from datetime import datetime
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("voucher_class").getOrCreate()


def check_str_to_date(str_date):
    try:
        datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


def calculate_frequency_segment(total_orders):
    if 0 <= total_orders <= 4:
        return '0-4'
    elif 5 <= total_orders <= 13:
        return '5-13'
    elif 14 <= total_orders <= 37:
        return '14-37'
    else:
        return 'undefined'


def calculate_recency_segment(last_order_ts):
    datediff = calculate_datediff(last_order_ts)

    if 30 <= datediff <= 60:
        return '30-60'
    elif 61 <= datediff <= 90:
        return '61-90'
    elif 91 <= datediff <= 120:
        return '91-120'
    elif 121 <= datediff <= 180:
        return '121-180'
    elif datediff > 180:
        return '180+'
    else:
        return 'undefined'


def calculate_datediff(last_order_ts):
    last_order = datetime.strptime(last_order_ts, '%Y-%m-%d %H:%M:%S')
    datediff = datetime.utcnow() - last_order
    return datediff.days


def get_voucher_amount(segment_name, segment_value):
    path = f'data/output/{segment_name}'
    segments_df = spark.read.parquet(path).where(f"segment_name = '{segment_value}'")
    if segments_df.count() > 0:
        voucher_amount = segments_df.first()['voucher_amount']
        return voucher_amount
    else:
        return None
