import unittest

from kitchen import process_order

'''
    Some considerations:
    (1) There are not any valid tests as no true output sample has been provided to compare to.
    Some tests are implemented for the sake of testing but with generated output in the context of
    the exercise.
'''

CSV_SOURCE='orders.csv'

# Note: This test is not valid in the context of the system but in the context
# of the exercise
class TestFormat(unittest.TestCase):
    def test_output_format(self):
        output_orders = process_order(CSV_SOURCE)
        for output_order in output_orders:
            self.assertRegex(output_order, r'R\d+,O\d+,\w+,\d+')

'''
    Instructions:
    python basic_test.py
    python -m basic_test --v
'''
if __name__ == '__main__':
    unittest.main()
