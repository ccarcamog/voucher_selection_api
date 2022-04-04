from flask import request, jsonify

from api import app
from api.model.Customer import Customer
from api.model.Voucher import Voucher


@app.get('/check_status')
def index():
    """Return a string

    Returns an active status, when flask project has been deployed successfully
    """
    return 'Active!'


@app.post("/voucher_segment_selector")
def voucher_segment_selector():
    """Return a Response type object, with JSON format, and number of server status

    Returns the formatted string, with human-readable version of opening hours
    using 12-hours clock
    """
    if request.is_json:
        input_json = request.get_json()
        customer_input = Customer(input_json)
        if customer_input.error_message == '':
            voucher_output = Voucher(customer_input)
            return jsonify(voucher_output.response), 201
        else:
            error_output = {
                'error_message': customer_input.error_message
            }
            return jsonify(error_output), 201
    return {"error": "Request must be JSON"}, 415
