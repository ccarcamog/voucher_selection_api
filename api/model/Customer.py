from schema import Schema
from api.model import utils


class Customer:
    """Class to include all needed methods for reading and transform
    JSON input and check schema.

    If the input schema sent in request
    does not mach with expected one, an error message will be sent as
    a response from the API
    """

    # Expected schema to be received by input JSON
    request_schema = Schema(
        {
            'customer_id': int,
            'country_code': str,
            'last_order_ts': str,
            'first_order_ts': str,
            'total_orders': int,
            'segment_name': str
        }
    )

    # Variable to store the segment mane received in input JSON
    segment_name = ''
    # Variable to store the calculated frequency segment received in input JSON
    frequent_segment = ''
    # Variable to store the calculated recency segment received in input JSON
    recency_segment = ''
    # Variable to store countries of interest in the voucher selection
    countries = ['Peru']
    # Variable to store valid segments
    segments = ['frequent_segment', 'recency_segment']
    # Variable to store any error message generated in any validation
    error_message = ''

    def __init__(self, json_input):
        """Class constructor

        Call all needed functions to read json input and format it before calculate response
        """
        # First validation is to check if input json complies with expected schema validation
        if not self.validate_json_input_schema(json_input):
            self.error_message = f'Request JSON does not complies with expected schema {self.request_schema}'
        # Then, check if containing data corresponds to expected one
        else:
            if self.validate_json_input_data(json_input):
                # Calculate segment value, according to segment name
                self.calculate_segment(json_input)
                # Fill segment name variable
                self.segment_name = json_input['segment_name']
                # Check if segment value is a valid one
                self.check_segment_value(json_input)
                # self.error_message = f'{self.frequent_segment} , {self.recency_segment}'

    def validate_json_input_schema(self, json_input):
        """Returns a boolean

        Checks if input JSON complies with expected schema
        """
        return self.request_schema.is_valid(json_input)

    def validate_json_input_data(self, json_input):
        """Returns a boolean

        Check fields needed to calculation of segments
        """
        if json_input['country_code'] not in self.countries:
            self.error_message = f"{json_input['country_code']} is not part of list of countries of interest."
            return False

        if json_input['segment_name'] not in self.segments:
            self.error_message = f"{json_input['segment_name']} is not part of list of valid segments."
            return False

        return True

    def calculate_segment(self, json_input):
        """Checks the segment name, and fill the corresponding segment into variable
        """
        if json_input['segment_name'] == 'frequent_segment':
            self.frequent_segment = utils.calculate_frequency_segment(json_input['total_orders'])
        elif json_input['segment_name'] == 'recency_segment':
            if utils.check_str_to_date(json_input['last_order_ts']):
                self.recency_segment = utils.calculate_recency_segment(json_input['last_order_ts'])
            else:
                self.error_message = f"{json_input['last_order_ts']} is not a valid date."

    def check_segment_value(self, json_input):
        if self.segment_name == 'frequent_segment' and self.frequent_segment == 'undefined':
            self.error_message = f"Segment not defined for {json_input['total_orders']} orders"
        elif self.segment_name == 'recency_segment' and self.recency_segment == 'undefined':
            self.error_message = f"Segment not defined for {utils.calculate_datediff(json_input['last_order_ts'])} " \
                                 f"days since last order"








