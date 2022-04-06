# Voucher Selection API
###### by Carlos Carcamo

The following project, is an HTTP API that takes an input JSON with information of clients vouchers transactions, for a delivery application, and returns the most used voucher amount for a specific segment.

## Project structure
As the main goal of the project is to deliver an API capable to respond to a specific client request, the project is divided in 3 different stages:
1. An Exploratory Data Analysis, performed in a `Jupyter Notebook`, using `Pandas`, to profile the input data (with is stored in `data/input/` folder).
2. A data pipeline, performed using `PySpark`
3. An API, developed using `Flask`

### Exploratory Data Analysis
As a first step, I started with a quick overview of the data. Before take any decision over the transformations and 
other technical aspects, for me is necessary to master the input data.

I chose `Jupiter Notebook` and `Pandas` for this purpose. `Jupiter Notebook` offers the advantage of see the result of every single transformation in a really 
quick way. It's outstanding to find patter or possible issues with data. Also, I chose `Pandas` because the set-up is easy, an offers all
the needed functions for exploration purposes. 

The final outcome of this profile, is stored in `eda` folder. You can check directly the `voucher_selection_eda.html` file. This file shows all the decision I took over cleaning tasks,
before starting to develop the data pipeline.

Summarizing, the transformation I found were necessary over input data are the following:
1. To meet part of the Acceptance Criteria of the project, filter dataset by `country_code` equals to `Peru`
2. Drop rows with null values
3. Drop duplicated rows
4. Drop rows with `total_orders` column with empty values
5. Cast `total_orders` column to `int` type
6. Cast `last_order_ts` and `timestamp` columns to `datetime64[ns, UTC]` type

### Data Pipeline development
After all the changes I identified in previous step, I decided to create a data pipeline to solve all the cleaning and filtering need of the data,
and also to simplify the API workload. 

The work of the data pipeline consist in the following steps:
1. Clean the data for all the issues found in EDA stage
2. Calculate segments for each transaction of the outcome dataset, after cleaning tasks
3. Aggregate data to calculate most used voucher amount for each calculated segment
4. Split the final outcome in two different datasets, one for frequent segment and another one for recency segment

Having the data aggregated in separate files, will simplify the workload of the API, as for each request, it will just query the data already aggregated,
instead of making the same calculations in every run.

I decided to use ```Apache Spark``` to reach this goal. `Apache Spark` is a really great solution to work with big datasets and deliver
results in acceptable timeframes. Also, is a scalable solution, as it can work in several cloud implementations, and also can be deployed into ``Databricks`` really easy. 

Also, pipes developed in `Apache Spark` can easy being scheduled using `Apache Airflow`, to keep the datasets updated.

The code for the data pipeline can be found in `data_pipe` folder.

_Important Note:_ Right now, the pipe need to be run manually (in order that this project represents a PoC phase).
A scheduling strategy needs to be implemented as the segment ``recency_segment`` relies on the datediff between last order date
for a client and current date. Basically, to update the segment, the pipe need to be executed at least once a day.

### Voucher Selection API
To accomplish the main goal of the project, I decided to use `Flask` as my API framework.

Flask is the lighter web framework provider I know,
It offers enough classes for why I intended to do and also a little number of dependencies to make it work.
Flask provides simplicity, flexibility and fine-grained control. It is unopinionated (it lets you decide how you want to implement things).

For this challenge, I will use 3 basic classes that `Flask` provides:

1. `flask`: To identify my code as an HTTP API project
2. `request`: To read the input JSON coming from each petition to the API
3. `jsonify`: To cast the output result of the API as a JSON response

#### Running the using Docker
1. Install ``Docker`` in your machine if you don't have it yet. You can check [here]('https://docs.docker.com/get-docker/) for more information about installation.
2. Clone project repo into your local from GitHub:
```bash
git clone https://github.com/ccarcamog/voucher_selection_api
```
3. Open a cmd/terminal window in your machine and navigate to the path you cloned the repo
4. Create ``Docker`` image in your local using this command:
```bash
docker compose up
```
Docker will start to download the all needed packages: An OS image (``alpine``), Java 11 and Python.
Then, It will start to install all Python libs needed to execute the API. Finally, it will
start the API. In te console/terminal you should see something like this:
```bash
voucher_selection_api-app-1  | ============================= test session starts ==============================
voucher_selection_api-app-1  | platform linux -- Python 3.9.7, pytest-7.1.1, pluggy-1.0.0
voucher_selection_api-app-1  | rootdir: /voucher_selection_api
voucher_selection_api-app-1  | plugins: mock-3.7.0, cov-3.0.0
voucher_selection_api-app-1  | collected 11 items
voucher_selection_api-app-1  | 
voucher_selection_api-app-1  | test/api_test.py ...........                                             [100%]
voucher_selection_api-app-1  | 
voucher_selection_api-app-1  | ----------- coverage: platform linux, python 3.9.7-final-0 -----------
voucher_selection_api-app-1  | Name                    Stmts   Miss  Cover
voucher_selection_api-app-1  | -------------------------------------------
voucher_selection_api-app-1  | api/__init__.py             3      0   100%
voucher_selection_api-app-1  | api/model/Customer.py      39      0   100%
voucher_selection_api-app-1  | api/model/Voucher.py       23      0   100%
voucher_selection_api-app-1  | api/model/utils.py         41     12    71%
voucher_selection_api-app-1  | api/views.py               18      0   100%
voucher_selection_api-app-1  | -------------------------------------------
voucher_selection_api-app-1  | TOTAL                     124     12    90%
voucher_selection_api-app-1  | 
voucher_selection_api-app-1  | 
voucher_selection_api-app-1  | ============================== 11 passed in 5.16s ==============================
voucher_selection_api-app-1  |  * Serving Flask app 'api' (lazy loading)
voucher_selection_api-app-1  |  * Environment: production
voucher_selection_api-app-1  |    WARNING: This is a development server. Do not use it in a production deployment.
voucher_selection_api-app-1  |    Use a production WSGI server instead.
voucher_selection_api-app-1  |  * Debug mode: off
voucher_selection_api-app-1  | WARNING: An illegal reflective access operation has occurred
voucher_selection_api-app-1  | WARNING: Illegal reflective access by org.apache.spark.unsafe.Platform (file:/usr/lib/python3.9/site-packages/pyspark/jars/spark-unsafe_2.12-3.2.1.jar) to constructor java.nio.DirectByteBuffer(long,int)
voucher_selection_api-app-1  | WARNING: Please consider reporting this to the maintainers of org.apache.spark.unsafe.Platform
voucher_selection_api-app-1  | WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
voucher_selection_api-app-1  | WARNING: All illegal access operations will be denied in a future release
voucher_selection_api-app-1  | Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
voucher_selection_api-app-1  | Setting default log level to "WARN".
voucher_selection_api-app-1  | To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
voucher_selection_api-app-1  | 22/04/06 05:47:56 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
voucher_selection_api-app-1  |  * Running on all addresses (0.0.0.0)
voucher_selection_api-app-1  |    WARNING: This is a development server. Do not use it in a production deployment.
voucher_selection_api-app-1  |  * Running on http://127.0.0.1:5000
voucher_selection_api-app-1  |  * Running on http://172.20.0.2:5000 (Press CTRL+C to quit)

```
API will be ready to be used, you can check it in another terminal (Or in an API platform like _Postman_), check the API status:
```bash
curl http://0.0.0.0:5001/check_status
```

You should receive an Active message:
```bash
Active!
```

#### Running the API manually without Docker
1. Install `python3` and `java 11` in your machine if you don't have it yet. You can check [here]('https://www.python.org/downloads/) for more information about installation.
2. Create a `virtualenv` from console and access it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Once inside venv, navigate to the folder you extracted the project:
```bash
cd {your_path}/voucher_selection_api
```
4. Install needed packages:
```bash
pip install -r requirements.txt
```
5. Create the following env variable:
```bash
export FLASK_APP=api
```
6. Run `flask`:
```bash
flask run
```
7. In another terminal (Or in an API platform like _Postman_), check the API status:
```bash
curl http://127.0.0.1:5000/check_status
```
You should receive an Active message:
```bash
Active!
```

#### HTTP API Endpoints
This API will handle 2 endpoints, one to check API status and the mainly one to process the input dataset.
##### `check_status` endpoint
Returns a string if API is running properly

As API status is a read-only operation, and no server resource will need to be modified, this is a `GET` method.

It does not need any parameter, just call it by its name:

```bash
curl http://127.0.0.1:5000/check_status
```
The output will be:
```bash
Active!
```

##### `voucher_segment_selector` endpoint
This is the main endpoint, which will be in charge to take the input JSON dataset and look for the most used voucher amount.

The input data, will use a series of methods and classes to search the desired data into the output datasets created by data pipeline. 
The API will generate a new resource that will be served as a response, that's why this is a `POST` method.

The input data will be sent in the request body as a raw element, always in `json` format. Here is an example of how to call it:

```bash
curl -i http://127.0.0.1:5000/voucher_segment_selector \
-X POST \
-H 'Content-Type: application/json' \
-d '{
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "frequent_segment"
}'
```
The API will read the `json` and start to process it to respond something like this:

```bash
HTTP/1.0 201 CREATED
Content-Type: application/json
...

{
    "voucher_amount": 2640.0
}
```

### Data Flow Process
The process of data transformation is really straightforward. Basically, the API follows the next steps for all incoming input JSON:
1. Read the `json` input
2. Creates an object `Client` basen on the `json` input.
3. Inside object `Client` input data will be validated to check if complies with expected schema, and data constrains as the country is `Peru`
4. Inside object `Client` the segment will be calculated, based on the data coming in the input data
5. If all validations passed, an object `Voucher` will be created, based in the object `Client` object validated before
6. Inside object `Voucher` the output datasets of data pipeline will be queried to look for voucher amount
7. The API will respond with object `Voucher` response