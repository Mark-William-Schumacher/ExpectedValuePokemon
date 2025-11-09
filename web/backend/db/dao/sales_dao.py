import sqlite3
from datetime import datetime
from textwrap import dedent

from . import queries


class SalesDAO:
    """
    Data Access Object for handling all sales-related database operations.
    """

    def __init__(self, conn):
        """
        Initializes the SalesDAO with a database connection.
        :param conn: An active database connection.
        """
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def add_sales_from_json(self, json_data):
        """
        Parses a JSON object and inserts the data into the respective sales tables
        using efficient bulk insertion.
        """
        card_id = self._extract_card_id(json_data)
        if not card_id:
            print("Error: Could not determine card_id from the JSON response.")
            return

        # 1. Upsert card_sales table
        self._upsert_card_sales(card_id, json_data.get('updated_date'))

        # 2. Bulk insert 'ebay_avg' data
        ebay_avg_data = json_data.get('ebay_avg', [])
        if ebay_avg_data:
            data_to_insert = [
                (card_id, self._parse_date(item.get('date_sold')), item.get('psa_grade'), item.get('sold_price'),
                 item.get('volume'))
                for item in ebay_avg_data
            ]
            self.cursor.executemany(queries.BULK_INSERT_EBAY_AVG, data_to_insert)
            print(f"Inserted {len(data_to_insert)} rows into ebay_avg.")

        # 3. Bulk insert 'tcgplayer' data
        tcgplayer_data = json_data.get('tcgplayer', [])
        if tcgplayer_data:
            data_to_insert = [
                (item.get('id'), card_id, self._parse_date(item.get('created_at')),
                 self._parse_date(item.get('date_sold')), item.get('interpolated'), item.get('set_id'),
                 item.get('sold_price'))
                for item in tcgplayer_data
            ]
            self.cursor.executemany(queries.BULK_INSERT_TCGPLAYER, data_to_insert)
            print(f"Inserted {len(data_to_insert)} rows into tcgplayer.")

        # 4. Bulk insert 'transactions' data
        transactions_data = json_data.get('transactions', [])
        if transactions_data:
            data_to_insert = [
                (item.get('id'), card_id, self._parse_date(item.get('date_sold')), item.get('ebay_handle'),
                 item.get('ebay_item_id'), item.get('marketplace'), item.get('num_bids'), item.get('psa_grade'),
                 item.get('set_id'), item.get('sold_price'), item.get('title'))
                for item in transactions_data
            ]
            self.cursor.executemany(queries.BULK_INSERT_TRANSACTIONS, data_to_insert)
            print(f"Inserted {len(data_to_insert)} rows into transactions.")

        # Commit all transactions at once
        self.conn.commit()
        print("Successfully added sales data to the database.")

        # After committing, update the sales volume for the affected card.
        if card_id:
            self.update_sales_volume(card_id)

    def update_sales_volume(self, card_id):
        """
        Calculates and updates the sales volume for a specific card based on
        a 30-day window from its most recent sale.
        """
        # 1. Find the most recent sale date for the card
        max_date_query = "SELECT MAX(date(date_sold)) as max_date FROM transactions WHERE card_id = ?"
        self.cursor.execute(max_date_query, (card_id,))
        max_date_row = self.cursor.fetchone()

        if not max_date_row or not max_date_row['max_date']:
            return  # No sales found

        last_sales_date = max_date_row['max_date']

        # 2. Calculate volumes within the 30-day window leading up to the last sale
        volume_query = dedent("""
        SELECT
            SUM(CASE WHEN psa_grade = 10.0 THEN 1 ELSE 0 END) as psa10_volume,
            SUM(CASE WHEN psa_grade >= 0.0 AND psa_grade < 10.0 THEN 1 ELSE 0 END) as non_psa10_volume
        FROM transactions
        WHERE card_id = ? AND date(date_sold) BETWEEN date(?, '-30 days') AND ?
                """)

        self.cursor.execute(volume_query, (card_id, last_sales_date, last_sales_date))
        volume_data = self.cursor.fetchone()

        psa10_volume = volume_data['psa10_volume'] if volume_data and volume_data['psa10_volume'] is not None else 0
        non_psa10_volume = volume_data['non_psa10_volume'] if volume_data and volume_data[
            'non_psa10_volume'] is not None else 0

        # 3. Upsert the results into the sales_volume table
        upsert_query = dedent("""
               INSERT INTO sales_volume (card_id, psa10_volume, non_psa10_volume, last_sales_date, last_calculated)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(card_id) DO UPDATE SET
                   psa10_volume = excluded.psa10_volume,
                   non_psa10_volume = excluded.non_psa10_volume,
                   last_sales_date = excluded.last_sales_date,
                   last_calculated = excluded.last_calculated;
           """)
        self.cursor.execute(upsert_query, (card_id, psa10_volume, non_psa10_volume, last_sales_date))
        self.conn.commit()
        print(f"Updated sales volume for card_id {card_id}.")

    def _extract_card_id(self, json_data):
        """Helper to consistently extract the card_id from the JSON response."""
        if json_data.get('transactions'):
            return json_data['transactions'][0].get('card_id')
        if json_data.get('tcgplayer'):
            return json_data['tcgplayer'][0].get('card_id')
        return None

    def _upsert_card_sales(self, card_id, updated_date_str):
        """Helper to handle the insert/update logic for the card_sales table."""
        self.cursor.execute(queries.UPSERT_CARD_SALES, (card_id,))
        if updated_date_str:
            updated_date_dt = datetime.strptime(updated_date_str, '%Y-%m-%d %H:%M:%S')
            self.cursor.execute(queries.UPDATE_CARD_SALES_DATE, (updated_date_dt, card_id))
        print(f"Upserted card_id {card_id} into card_sales.")

    def get_sales_as_json(self, card_id):
        """
        Retrieves all sales data for a given card_id from the database
        and reconstructs it into a JSON-like dictionary format.

        :param card_id: The card_id to retrieve data for.
        :return: A dictionary matching the original JSON structure, or None if not found.
        """
        # Fetch the main card sale information first.
        card_sale_row = self.cursor.execute(queries.SELECT_CARD_SALES_BY_ID, (card_id,)).fetchone()
        if not card_sale_row:
            return None  # Return None if the card_id doesn't exist.

        # Start building the result dictionary.
        result = {
            # Format the updated_date back to the expected string format.
            "updated_date": card_sale_row["updated_date"].strftime('%Y-%m-%d %H:%M:%S')
        }

        # Fetch and reconstruct the 'ebay_avg' list.
        ebay_avg_rows = self.cursor.execute(queries.SELECT_EBAY_AVG_BY_ID, (card_id,)).fetchall()
        result['ebay_avg'] = [
            {
                "date_sold": self._format_date_for_json(row["date_sold"]),
                "psa_grade": row["psa_grade"],
                "sold_price": row["sold_price"],
                "volume": row["volume"]
            } for row in ebay_avg_rows
        ]

        # Fetch and reconstruct the 'tcgplayer' list.
        tcgplayer_rows = self.cursor.execute(queries.SELECT_TCGPLAYER_BY_ID, (card_id,)).fetchall()
        result['tcgplayer'] = [
            {
                "id": row["source_tcgplayer_id"],
                "card_id": row["card_id"],
                "created_at": self._format_date_for_json(row["created_at"]),
                "date_sold": self._format_date_for_json(row["date_sold"]),
                "interpolated": bool(row["interpolated"]),
                "set_id": row["set_id"],
                "sold_price": row["sold_price"]
            } for row in tcgplayer_rows
        ]

        # Fetch and reconstruct the 'transactions' list.
        transaction_rows = self.cursor.execute(queries.SELECT_TRANSACTIONS_BY_ID, (card_id,)).fetchall()
        result['transactions'] = [
            {
                "id": row["source_transaction_id"],
                "card_id": row["card_id"],
                "date_sold": self._format_date_for_json(row["date_sold"]),
                "ebay_handle": row["ebay_handle"],
                "ebay_item_id": row["ebay_item_id"],
                "marketplace": row["marketplace"],
                "num_bids": row["num_bids"],
                "psa_grade": row["psa_grade"],
                "set_id": row["set_id"],
                "sold_price": row["sold_price"],
                "title": row["title"]
            } for row in transaction_rows
        ]

        # The 'page' key was in the original JSON, so we add it back for consistency.
        result['page'] = 0

        return result


    def _parse_date(self, date_string):
        """
        Helper to parse date strings from the JSON response.
        """
        if not date_string:
            return None
        # The 'GMT' timezone name can be inconsistent, so we remove it before parsing.
        if date_string.endswith(' GMT'):
            date_string = date_string[:-4]
        try:
            return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S')
        except ValueError:
            print(f"Warning: Could not parse date '{date_string}'. Skipping.")
            return None

    def _format_date_for_json(self, dt):
        """
        Helper to format datetime objects back to the string format expected in the JSON.
        Example: 'Fri, 04 Jul 2025 00:00:00 GMT'
        """
        if not dt:
            return None
        # This format includes the literal 'GMT' at the end.
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
