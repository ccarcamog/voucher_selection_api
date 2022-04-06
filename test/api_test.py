from json import loads
from api import app

mock_header = {
    "Content-Type": "test",
}

mock_request_success_frequent_segment = {
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "frequent_segment"
}

mock_request_success_frequent_segment_undefined = {
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 50,
    "segment_name": "frequent_segment"
}

mock_request_success_recency_segment = {
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "recency_segment"
}

mock_request_wrong_country = {
    "customer_id": 123,
    "country_code": "El Salvador",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "recency_segment"
}

mock_request_wrong_segment = {
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "2021-01-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "test_segment"
}

mock_request_invalid_last_order_ts = {
    "customer_id": 123,
    "country_code": "Peru",
    "last_order_ts": "test",
    "first_order_ts": "2017-05-03 00:00:00",
    "total_orders": 5,
    "segment_name": "recency_segment"
}

mock_request_bad = {
    "test": 1
}


def test_check_status():
    response = app.test_client().get('/check_status')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Active!'


def test_voucher_segment_selector_success_request_frequent_segment(mocker):
    # Mocking response of method that reads data with spark
    mocker.patch('api.model.utils.get_voucher_amount', return_value=1)
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_success_frequent_segment)
    res = loads(response.data.decode('utf-8')).get('voucher_amount')
    assert response.status_code == 201
    assert res == 1


def test_voucher_segment_selector_success_request_recency_segment(mocker):
    # Mocking response of method that reads data with spark
    mocker.patch('api.model.utils.get_voucher_amount', return_value=1)
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_success_recency_segment)
    res = loads(response.data.decode('utf-8')).get('voucher_amount')
    assert response.status_code == 201
    assert res == 1


def test_voucher_segment_selector_non_json_request():
    response = app.test_client().post('/voucher_segment_selector', json='test', headers=mock_header)
    assert response.status_code == 415


def test_voucher_segment_selector_invalid_json_schema():
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_bad)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert 'Request JSON does not complies with expected schema' in res


def test_voucher_segment_selector_not_found_segment(mocker):
    # Mocking response of method that reads data with spark
    mocker.patch('api.model.utils.get_voucher_amount', return_value=None)
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_success_frequent_segment)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert 'No voucher_amount found for segment' in res


def test_voucher_segment_selector_wrong_country():
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_wrong_country)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert res.endswith('is not part of list of countries of interest.')


def test_voucher_segment_selector_wrong_segment():
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_wrong_segment)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert res.endswith('is not part of list of valid segments.')


def test_voucher_segment_selector_invalid_last_order_ts():
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_invalid_last_order_ts)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert res.endswith('is not a valid date.')


def test_voucher_segment_selector_undefined_frequent_segment():
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_success_frequent_segment_undefined)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert 'Segment not defined for' in res
    assert res.endswith('orders')


def test_voucher_segment_selector_undefined_recency_segment(mocker):
    # Mocking response of method that reads data with spark
    mocker.patch('api.model.utils.calculate_datediff', return_value=1)
    response = app.test_client().post('/voucher_segment_selector', json=mock_request_success_recency_segment)
    res = loads(response.data.decode('utf-8')).get('error_message')
    assert response.status_code == 201
    assert 'Segment not defined for' in res
    assert res.endswith('days since last order')
