"""
PostgreSQL Database to JSON Exporter - Filtered Fields
Extracts specific fields from MSIG travel insurance claims data
"""

try:
    import psycopg2 as psycopg
    PSYCOPG_VERSION = 2
except ImportError:
    try:
        import psycopg
        PSYCOPG_VERSION = 3
    except ImportError:
        raise ImportError(
            "Please install either 'psycopg2-binary' or 'psycopg[binary]'")

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List
import os


class DatabaseToJSONExporter:
    """Export PostgreSQL database tables to JSON format"""

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize database connection

        Args:
            db_config: Dictionary with keys: host, port, database, user, password
        """
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            if PSYCOPG_VERSION == 2:
                self.connection = psycopg.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    database=self.db_config['database'],
                    user=self.db_config['user'],
                    password=self.db_config['password'])
            else:  # psycopg version 3
                conn_string = f"host={self.db_config['host']} port={self.db_config['port']} dbname={self.db_config['database']} user={self.db_config['user']} password={self.db_config['password']}"
                self.connection = psycopg.connect(conn_string)

            self.cursor = self.connection.cursor()
            print(f"✓ Connected to database: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✓ Database connection closed")

    def _serialize_value(self, value: Any) -> Any:
        """Convert non-JSON-serializable types to JSON-compatible formats"""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif value is None:
            return None
        else:
            return value

    def export_filtered_data(self,
                            schema: str,
                            table: str,
                            output_file: str,
                            columns: List[str],
                            limit: int = None,
                            pretty: bool = True):
        """
        Export only specified columns to JSON file

        Args:
            schema: Database schema name
            table: Table name
            output_file: Output JSON file path
            columns: List of column names to export
            limit: Optional limit on number of rows
            pretty: Whether to format JSON with indentation
        """
        print(f"\nExporting {schema}.{table} (filtered columns)...")
        print(f"  Columns: {', '.join(columns)}")

        # Build and execute query with specified columns
        query = f"SELECT {', '.join(columns)} FROM {schema}.{table}"
        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for col_name, value in zip(columns, row):
                row_dict[col_name] = self._serialize_value(value)
            data.append(row_dict)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"  ✓ Exported {len(data)} rows")
        print(f"  File: {output_file} ({file_size:.2f} KB)")


# ==================== USAGE ====================


def main():
    """Main execution function"""

    # Database configuration
    DB_CONFIG = {
        'host': 'hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com',
        'port': '5432',
        'database': 'hackathon_db',
        'user': 'hackathon_user',
        'password': 'Hackathon2025!'
    }

    # Schema and table
    SCHEMA = 'hackathon'
    TABLE = 'claims'

    # Define the specific columns to export
    COLUMNS_TO_EXPORT = [
        'accident_date',
        'destination',
        'claim_type',
        'cause_of_loss',
        'loss_type',
        'gross_paid'
    ]

    # Initialize exporter
    exporter = DatabaseToJSONExporter(DB_CONFIG)

    try:
        # Connect to database
        if not exporter.connect():
            return

        # Export filtered data
        print("\n" + "=" * 70)
        print("EXPORTING FILTERED CLAIMS DATA")
        print("=" * 70)
        exporter.export_filtered_data(
            schema=SCHEMA,
            table=TABLE,
            output_file='claims_data.json',
            columns=COLUMNS_TO_EXPORT
            # limit=100  # Uncomment to limit rows
        )

    except Exception as e:
        print(f"\n✗ Error during export: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Always disconnect
        exporter.disconnect()


if __name__ == "__main__":
    print("=" * 70)
    print("MSIG TRAVEL INSURANCE CLAIMS - FILTERED EXPORT")
    print("=" * 70)
    main()