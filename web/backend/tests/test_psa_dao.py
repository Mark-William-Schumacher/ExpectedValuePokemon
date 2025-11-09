import json
import os
import sqlite3
import unittest
from datetime import datetime

from web.backend.db.dao.psa_dao import PsaDAO
from web.backend.db.database_setup import setup_schema
from web.backend.db.db_config import configure_sqlite_for_project

# Configure the SQLite environment for the test run.
configure_sqlite_for_project()


class TestPsaDAO(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh in-memory database and DAO for each test.
        This method is run before each test function.
        """
        self.maxDiff = None
        # 1. Create a temporary, in-memory SQLite database.
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)

        # 2. Create all tables from the schema.
        setup_schema(self.conn)

        # 3. Instantiate the DAO with the in-memory database connection.
        self.psa_dao = PsaDAO(self.conn)

        # 4. Define the sample JSON data for the PSA population test.
        self.sample_psa_pop_json = {
            "1.0": 0, "1.5": 0, "2.0": 0, "2.5": 0, "3.0": 3, "3.5": 0,
            "4.0": 4, "4.5": 0, "5.0": 13, "5.5": 0, "6.0": 30, "6.5": 0,
            "7.0": 104, "7.5": 0, "8.0": 618, "8.5": 2, "9.0": 1957, "10.0": 647,
            "updated_date": "2025-09-06 18:37:39"
        }

        # 5. Create prerequisite data to satisfy foreign key constraints.
        cursor = self.conn.cursor()
        # Create a dummy set.
        cursor.execute("INSERT INTO sets (set_id, name, code) VALUES (?, ?, ?)", (1, 'Test Set', 'TST'))
        # Create a dummy card associated with the dummy set.
        cursor.execute("INSERT INTO cards (card_id, set_id, name) VALUES (?, ?, ?)", (41324, 1, 'Test Card'))
        self.conn.commit()

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.conn.close()

    def test_add_psa_population_from_json(self):
        """
        Tests that add_psa_population_from_json correctly unpivots the JSON
        and inserts the data into the 'psa_population' table.
        """
        # 1. Execute the method we want to test.
        test_card_id = 41324
        self.psa_dao.add_psa_population_from_json(test_card_id, self.sample_psa_pop_json)

        # 2. Verification step: Query the database.
        cursor = self.conn.cursor()

        # Check that the correct number of rows were inserted (18 grades in the JSON).
        cursor.execute("SELECT COUNT(*) FROM psa_population WHERE card_id = ?", (test_card_id,))
        self.assertEqual(cursor.fetchone()[0], 18)

        # Verify a specific entry (e.g., PSA 9).
        cursor.execute("SELECT psa_grade, population_count, updated_date FROM psa_population WHERE card_id = ? AND psa_grade = ?", (test_card_id, 9.0))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 9.0)
        self.assertEqual(row[1], 1957)
        self.assertEqual(row[2], datetime(2025, 9, 6, 18, 37, 39))

    def test_get_psa_population_as_json(self):
        """
        Tests that get_psa_population_as_json can accurately reconstruct the
        "wide" JSON format from the "long" database format.
        """
        # 1. Insert the data from the test JSON.
        test_card_id = 41324
        self.psa_dao.add_psa_population_from_json(test_card_id, self.sample_psa_pop_json)

        # 2. Retrieve the data using the new function.
        reconstructed_data = self.psa_dao.get_psa_population_as_json(test_card_id)

        # 3. Verify that the reconstructed data matches the original input.
        self.assertDictEqual(reconstructed_data, self.sample_psa_pop_json)
