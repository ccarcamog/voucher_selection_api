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

#### Running the API
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
<p>Returns a string if API is running properly</p>
As API status is a read-only operation, and no server resource will need to be modified, this is a `GET` method.
<p>It does not need any parameter, just call it by its name:</p>

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