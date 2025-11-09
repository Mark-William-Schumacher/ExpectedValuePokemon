import os
import unittest
import sqlite3
import json
from datetime import datetime

# Adjust the import paths based on the test runner's root directory
# Assuming the tests are run from the project root.
from web.backend.db.dao.sales_dao import SalesDAO
from web.backend.db.database_setup import setup_schema
from web.backend.db.db_config import configure_sqlite_for_project

# Configure the SQLite environment for the test run.
configure_sqlite_for_project()


class TestSalesDAO(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh in-memory database and DAO for each test.
        This method is run before each test function.
        """
        # 1. Create a temporary, in-memory SQLite database.
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)

        # 2. Create the tables using our existing schema setup function.
        setup_schema(self.conn)

        # 3. Instantiate the DAO with the in-memory database connection.
        self.sales_dao = SalesDAO(self.conn)

        # 4. Load sample JSON data for our tests from the resources file.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(test_dir, 'resources', 'test_get_volume_of_transactions_card_id=41324.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            self.sample_json_data = json.load(f)

    def tearDown(self):
        """
        Clean up after each test.
        This method is run after each test function.
        """
        self.conn.close()

    def test_add_sales_from_json(self):
        """
        Tests that add_sales_from_json correctly inserts data into all relevant tables.
        """
        # Execute the method we want to test
        self.sales_dao.add_sales_from_json(self.sample_json_data)

        # Verification step: Query the database to ensure data was inserted correctly.
        cursor = self.conn.cursor()

        # 1. Verify 'card_sales' table
        cursor.execute("SELECT card_id, updated_date FROM card_sales")
        card_sale_row = cursor.fetchone()
        self.assertIsNotNone(card_sale_row)
        self.assertEqual(card_sale_row[0], 41324)  # Assert against the card_id from the JSON file
        self.assertEqual(card_sale_row[1], datetime(2025, 9, 5, 18, 3, 50))  # Assert against the updated_date from the file

        # 2. Verify 'ebay_avg' table has the correct number of entries
        cursor.execute("SELECT COUNT(*) FROM ebay_avg")
        self.assertEqual(cursor.fetchone()[0], 7)

        # 3. Verify 'tcgplayer' table has the correct number of entries
        cursor.execute("SELECT COUNT(*) FROM tcgplayer")
        self.assertEqual(cursor.fetchone()[0], 9)

        # 4. Verify 'transactions' table has the correct number of entries
        cursor.execute("SELECT COUNT(*) FROM transactions")
        self.assertEqual(cursor.fetchone()[0], 7)

    def test_add_sales_from_json_is_idempotent(self):
        """
        Tests that calling add_sales_from_json multiple times does not create duplicate entries.
        """
        # Execute the method once and check the initial count.
        self.sales_dao.add_sales_from_json(self.sample_json_data)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        initial_count = cursor.fetchone()[0]
        self.assertEqual(initial_count, 7)

        # Execute the method a second time.
        self.sales_dao.add_sales_from_json(self.sample_json_data)

        # Verify that the count has not changed.
        cursor.execute("SELECT COUNT(*) FROM transactions")
        second_count = cursor.fetchone()[0]
        self.assertEqual(second_count, initial_count)

    def test_add_sales_from_large_json_file(self):
        """
        Tests that add_sales_from_json correctly handles a large volume of data
        and inserts the expected number of rows into each table.
        """
        # 1. Load the large JSON test file.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(test_dir, 'resources', 'test_2_get_volume_of_transactions_large_file.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            large_json_data = json.load(f)

        # 2. Execute the method with the large dataset.
        self.sales_dao.add_sales_from_json(large_json_data)

        # 3. Verification step: Query the database to ensure counts are correct.
        cursor = self.conn.cursor()

        # Verify 'transactions' table count
        cursor.execute("SELECT COUNT(*) FROM transactions")
        self.assertEqual(cursor.fetchone()[0], 3375, "Incorrect row count in 'transactions' table.")

        # Verify 'tcgplayer' table count
        cursor.execute("SELECT COUNT(*) FROM tcgplayer")
        self.assertEqual(cursor.fetchone()[0], 353, "Incorrect row count in 'tcgplayer' table.")

        # Verify 'ebay_avg' table count
        cursor.execute("SELECT COUNT(*) FROM ebay_avg")
        self.assertEqual(cursor.fetchone()[0], 3650, "Incorrect row count in 'ebay_avg' table.")


    def test_get_sales_as_json(self):
        """
        Tests that get_sales_as_json can accurately reconstruct the data
        that was previously inserted.
        """
        # 1. Insert the data from the small test file.
        self.sales_dao.add_sales_from_json(self.sample_json_data)

        # 2. Retrieve the data using the new function.
        reconstructed_data = self.sales_dao.get_sales_as_json(41324)

        # 3. Verify that the reconstructed data matches the original input.
        # We use assertDictEqual for a detailed comparison.
        self.assertDictEqual(reconstructed_data, self.sample_json_data)



if __name__ == '__main__':
    unittest.main()
