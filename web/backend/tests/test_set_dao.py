import json
import os
import sqlite3
import unittest
from datetime import datetime

from web.backend.db.dao.set_dao import SetDAO
from web.backend.db.database_setup import setup_schema
from web.backend.db.db_config import configure_sqlite_for_project

# Configure the SQLite environment for the test run.
configure_sqlite_for_project()


class TestSetDAO(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        """
        Set up a fresh in-memory database and DAO for each test.
        """
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        setup_schema(self.conn)
        self.set_dao = SetDAO(self.conn)

        # Load sample JSON data for tests
        test_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(test_dir, 'resources', 'test_short_get_card_prices_setId=557.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            self.sample_json_data = json.load(f)

        # Load sample JSON data for set details tests
        set_details_json_path = os.path.join(test_dir, 'resources', 'set_details=get_all_sets.json')
        with open(set_details_json_path, 'r', encoding='utf-8') as f:
            self.set_details_json_data = json.load(f)

        # Load large set details json
        large_set_details_json_path = os.path.join(test_dir, 'resources', 'large_set_details=get_all_sets.json')
        with open(large_set_details_json_path, 'r', encoding='utf-8') as f:
            self.large_set_details_json_data = json.load(f)


    def tearDown(self):
        """
        Clean up after each test.
        """
        self.conn.close()

    def test_add_set_from_json(self):
        """
        Tests that add_set_from_json correctly inserts data into all relevant tables.
        """
        self.set_dao.add_set_from_json(self.sample_json_data)
        cursor = self.conn.cursor()

        # 1. Verify 'sets' table
        cursor.execute("SELECT set_id, name, code, updated_date FROM sets")
        set_row = cursor.fetchone()
        self.assertIsNotNone(set_row)
        self.assertEqual(set_row[0], 557)
        self.assertEqual(set_row[1], "Prismatic Evolutions")
        self.assertEqual(set_row[2], "PRE")
        self.assertEqual(set_row[3], datetime(2025, 9, 11, 20, 19, 48))

        # 2. Verify 'cards' table has the correct number of entries (8 cards in JSON)
        cursor.execute("SELECT COUNT(*) FROM cards")
        self.assertEqual(cursor.fetchone()[0], 8)

        # 3. Verify 'card_stats' table has the correct total number of stats (40 stats in JSON)
        cursor.execute("SELECT COUNT(*) FROM card_stats")
        self.assertEqual(cursor.fetchone()[0], 40)

    def test_add_set_from_json_is_idempotent(self):
        """
        Tests that calling add_set_from_json multiple times does not create duplicate entries.
        """
        # Execute the method once and check initial counts
        self.set_dao.add_set_from_json(self.sample_json_data)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards")
        initial_card_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM card_stats")
        initial_stats_count = cursor.fetchone()[0]

        self.assertEqual(initial_card_count, 8)
        self.assertEqual(initial_stats_count, 40)

        # Execute the method a second time
        self.set_dao.add_set_from_json(self.sample_json_data)

        # Verify that the counts have not changed
        cursor.execute("SELECT COUNT(*) FROM cards")
        second_card_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM card_stats")
        second_stats_count = cursor.fetchone()[0]

        self.assertEqual(second_card_count, initial_card_count)
        self.assertEqual(second_stats_count, initial_stats_count)

    def test_get_set_as_json(self):
        """
        Tests that get_set_as_json can accurately reconstruct the data
        that was previously inserted.
        """
        # 1. Insert the data from the test file.
        self.set_dao.add_set_from_json(self.sample_json_data)

        # 2. Retrieve the data using the new function for set_id 557.
        reconstructed_data = self.set_dao.get_set_as_json(557)

        # 3. Verify that the reconstructed data matches the original input.
        # We need to sort the inner lists to ensure a consistent comparison
        # since database queries do not guarantee order.
        self.sample_json_data['data'].sort(key=lambda x: x['id'])
        reconstructed_data['data'].sort(key=lambda x: x['id'])
        for card in self.sample_json_data['data']:
            card['stats'].sort(key=lambda x: x['source'])
        for card in reconstructed_data['data']:
            card['stats'].sort(key=lambda x: x['source'])

        self.assertDictEqual(reconstructed_data, self.sample_json_data)
        print("Test passed!")

    def test_add_set_from_large_json(self):
        """
        Tests that add_set_from_json correctly handles a large volume of data
        from 'test_2_large_get_card_prices_setId=557.json' and inserts the
        expected number of rows (447) into the 'cards' table.
        """
        # 1. Load the large JSON test file.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(test_dir, 'resources', 'test_2_large_get_card_prices_setId=557.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            large_json_data = json.load(f)

        # 2. Execute the method with the large dataset.
        self.set_dao.add_set_from_json(large_json_data)

        # 3. Verification step: Query the database to ensure the card count is correct.
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards")
        self.assertEqual(cursor.fetchone()[0], 447, "Incorrect row count in 'cards' table for the large dataset.")

    def test_add_set_details_from_json(self):
        """
        Tests that add_set_details_from_json correctly inserts data into
        the 'sets' and 'set_details' tables.
        """
        self.set_dao.add_set_details_from_json(self.set_details_json_data)
        cursor = self.conn.cursor()

        # 1. Verify 'sets' table has the correct number of entries
        cursor.execute("SELECT COUNT(*) FROM sets")
        self.assertEqual(cursor.fetchone()[0], 5)

        # 2. Verify 'set_details' table has the correct number of entries
        cursor.execute("SELECT COUNT(*) FROM set_details")
        self.assertEqual(cursor.fetchone()[0], 5)

        # 3. Verify a specific entry in 'set_details'
        cursor.execute("SELECT set_id, language, release_date, updated_date FROM set_details WHERE set_id = 571")
        set_details_row = cursor.fetchone()
        self.assertIsNotNone(set_details_row)
        self.assertEqual(set_details_row[0], 571)
        self.assertEqual(set_details_row[1], "ENGLISH")
        self.assertEqual(set_details_row[2], datetime(2025, 7, 18, 0, 0, 0))
        self.assertEqual(set_details_row[3], datetime(2025, 9, 5, 22, 38, 6))

        # 4. Verify that the corresponding 'updated_date' in 'sets' is NULL
        cursor.execute("SELECT updated_date FROM sets WHERE set_id = 571")
        sets_row = cursor.fetchone()
        self.assertIsNone(sets_row[0])

    def test_get_set_details_as_json(self):
        """
        Tests that get_set_details_as_json can accurately reconstruct
        the data that was previously inserted.
        """
        # 1. Insert the data from the set details file.
        self.set_dao.add_set_details_from_json(self.set_details_json_data)

        # 2. Retrieve the data for a specific set_id.
        reconstructed_data = self.set_dao.get_set_details_as_json(571)

        # 3. Construct the expected output dictionary.
        expected_data = {
            "id": 571,
            "name": "White Flare",
            "code": None,
            "language": "ENGLISH",
            "release_date": "Fri, 18 Jul 2025 00:00:00 GMT",
            "card_info_updated_date": None,
            "set_details_updated_date": "2025-09-05 22:38:06"
        }

        # 4. Verify that the reconstructed data matches the expected dictionary.
        self.assertDictEqual(reconstructed_data, expected_data)

    def test_add_set_details_from_large_json(self):
        """
        Tests that add_set_details_from_json correctly handles a large volume of data.
        """
        # 1. Execute the method with the large dataset.
        self.set_dao.add_set_details_from_json(self.large_set_details_json_data)

        # 2. Verification step: Query the database to ensure counts are correct.
        cursor = self.conn.cursor()

        # Verify 'sets' table count
        cursor.execute("SELECT COUNT(*) FROM sets")
        self.assertEqual(cursor.fetchone()[0], 174, "Incorrect row count in 'sets' table.")

        # Verify 'set_details' table count
        cursor.execute("SELECT COUNT(*) FROM set_details")
        self.assertEqual(cursor.fetchone()[0], 174, "Incorrect row count in 'set_details' table.")

    def test_add_set_from_json_updates_existing_data(self):
        """
        Tests that calling add_set_from_json with updated data correctly
        overwrites the existing records in the database.
        """
        # --- 1. Initial Insert ---
        # Make a deep copy to avoid modifying the original test data
        initial_data = json.loads(json.dumps(self.sample_json_data))
        self.set_dao.add_set_from_json(initial_data)

        cursor = self.conn.cursor()

        # --- 2. Verify Initial State ---
        # Check the name of a specific card (id=41001) from the initial data.
        cursor.execute("SELECT name FROM cards WHERE card_id = 73053")
        initial_name = cursor.fetchone()[0]
        self.assertEqual(initial_name, "Amarys")

        # --- 3. Create Updated Data ---
        # Create a modified version of the JSON with an updated name for the same card.
        updated_data = json.loads(json.dumps(initial_data))
        updated_data['data'][0]['name'] = "Updated Dratini"  # Card with id 41001 is the first in the list
        updated_data['data'][0]['stats'][0]['avg'] = 999.99  # Update a stat as well

        # --- 4. Second Insert (should trigger an upsert) ---
        self.set_dao.add_set_from_json(updated_data)

        # --- 5. Verify Updated State ---
        # Verify that the card's name has been updated.
        cursor.execute("SELECT name FROM cards WHERE card_id = 73053")
        updated_name = cursor.fetchone()[0]
        self.assertEqual(updated_name, "Updated Dratini")

        # Verify that the card's stat has been updated.
        cursor.execute("SELECT avg FROM card_stats WHERE card_id = 73053")
        updated_avg = cursor.fetchone()[0]
        self.assertEqual(updated_avg, 999.99)

        # Verify that no new rows were added to the tables.
        cursor.execute("SELECT COUNT(*) FROM cards")
        self.assertEqual(cursor.fetchone()[0], 8)
        cursor.execute("SELECT COUNT(*) FROM card_stats")
        self.assertEqual(cursor.fetchone()[0], 40)
        print("Upsert functionality verified successfully!")
