from api.model.Customer import Customer
from api.model import utils


class Voucher:
    """Class to include all needed methods for the creation of
    API response

    This class reads directly for the output data created by
    data pipeline
    """
    response = dict()
    segment_name = ''
    segment_value = ''
    voucher_amount = 0

    def __init__(self, customer: Customer):
        """Class constructor

        Call all needed functions to create json output with needed information
        """
        self.segment_name = customer.segment_name
        self.get_segment_value(customer)
        self.get_voucher_amount()
        self.create_response()

    def get_segment_value(self, customer):
        """No value is returned

        Gets the segment name and value from Customer class
        and adds it into class variables
        """
        if customer.segment_name == 'frequent_segment':
            self.segment_value = customer.frequent_segment
        elif customer.segment_name == 'recency_segment':
            self.segment_value = customer.recency_segment

    def get_voucher_amount(self):
        """No value is returned

        Gets value of voucher amount extracted from dataset
        created by data pipeline
        """
        self.voucher_amount = utils.get_voucher_amount(self.segment_name, self.segment_value)

    def create_response(self):
        """No value is returned

        Builds the response that will be responded by the API
        """
        if self.voucher_amount:
            self.response = {
                'voucher_amount': self.voucher_amount
            }
        else:
            self.response = {
                'error_message': f'No voucher_amount found for segment {self.segment_name} with value {self.segment_value}'
            }
