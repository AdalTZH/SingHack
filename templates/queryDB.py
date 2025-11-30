"""
PostgreSQL Database to JSON Exporter
Extracts MSIG travel insurance claims data from RDS PostgreSQL database
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

    def get_table_columns(self, schema: str, table: str) -> List[str]:
        """Get column names for a table"""
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        self.cursor.execute(query, (schema, table))
        columns = [row[0] for row in self.cursor.fetchall()]
        return columns

    def get_table_info(self, schema: str, table: str) -> Dict[str, Any]:
        """Get metadata about the table"""
        # Get row count
        count_query = f'SELECT COUNT(*) FROM {schema}.{table}'
        self.cursor.execute(count_query)
        row_count = self.cursor.fetchone()[0]

        # Get column info
        columns = self.get_table_columns(schema, table)

        return {
            'schema': schema,
            'table': table,
            'row_count': row_count,
            'column_count': len(columns),
            'columns': columns
        }

    def export_table_to_dict(self,
                             schema: str,
                             table: str,
                             limit: int = None) -> Dict[str, Any]:
        """
        Export a single table to dictionary format

        Args:
            schema: Database schema name
            table: Table name
            limit: Optional limit on number of rows to export

        Returns:
            Dictionary with metadata and data
        """
        print(f"\nExporting {schema}.{table}...")

        # Get table metadata
        metadata = self.get_table_info(schema, table)
        print(
            f"  Rows: {metadata['row_count']}, Columns: {metadata['column_count']}"
        )

        # Build query
        columns = metadata['columns']
        query = f"SELECT {', '.join(columns)} FROM {schema}.{table}"
        if limit:
            query += f" LIMIT {limit}"

        # Execute query
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for col_name, value in zip(columns, row):
                row_dict[col_name] = self._serialize_value(value)
            data.append(row_dict)

        print(f"  ✓ Exported {len(data)} rows")

        return {
            'metadata': metadata,
            'data': data,
            'exported_at': datetime.now().isoformat(),
            'exported_rows': len(data)
        }

    def export_to_json_file(self,
                            schema: str,
                            table: str,
                            output_file: str,
                            limit: int = None,
                            pretty: bool = True):
        """
        Export table directly to JSON file

        Args:
            schema: Database schema name
            table: Table name
            output_file: Output JSON file path
            limit: Optional limit on number of rows
            pretty: Whether to format JSON with indentation
        """
        # Export table data
        export_data = self.export_table_to_dict(schema, table, limit)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(export_data, f, ensure_ascii=False)

        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"\n✓ Exported to: {output_file}")
        print(f"  File size: {file_size:.2f} KB")

    def export_data_only(self,
                         schema: str,
                         table: str,
                         output_file: str,
                         limit: int = None,
                         pretty: bool = True):
        """
        Export only the data array (without metadata) to JSON file

        Args:
            schema: Database schema name
            table: Table name
            output_file: Output JSON file path
            limit: Optional limit on number of rows
            pretty: Whether to format JSON with indentation
        """
        print(f"\nExporting {schema}.{table} (data only)...")

        # Get columns
        columns = self.get_table_columns(schema, table)

        # Build and execute query
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

    def get_summary_statistics(self, schema: str,
                               table: str) -> Dict[str, Any]:
        """Get summary statistics for the claims table"""
        stats = {}

        # Total claims
        self.cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        stats['total_claims'] = self.cursor.fetchone()[0]

        # Claims by status
        self.cursor.execute(f"""
            SELECT claim_status, COUNT(*) as count 
            FROM {schema}.{table} 
            GROUP BY claim_status 
            ORDER BY count DESC
        """)
        stats['claims_by_status'] = [{
            'status': row[0],
            'count': row[1]
        } for row in self.cursor.fetchall()]

        # Claims by type
        self.cursor.execute(f"""
            SELECT claim_type, COUNT(*) as count 
            FROM {schema}.{table} 
            GROUP BY claim_type 
            ORDER BY count DESC
        """)
        stats['claims_by_type'] = [{
            'type': row[0],
            'count': row[1]
        } for row in self.cursor.fetchall()]

        # Total amounts
        self.cursor.execute(f"""
            SELECT 
                SUM(gross_incurred) as total_gross_incurred,
                SUM(gross_paid) as total_gross_paid,
                SUM(net_incurred) as total_net_incurred,
                SUM(net_paid) as total_net_paid
            FROM {schema}.{table}
        """)
        amounts = self.cursor.fetchone()
        stats['financial_summary'] = {
            'total_gross_incurred': self._serialize_value(amounts[0]),
            'total_gross_paid': self._serialize_value(amounts[1]),
            'total_net_incurred': self._serialize_value(amounts[2]),
            'total_net_paid': self._serialize_value(amounts[3])
        }

        # Top destinations
        self.cursor.execute(f"""
            SELECT destination, COUNT(*) as count 
            FROM {schema}.{table} 
            GROUP BY destination 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats['top_destinations'] = [{
            'destination': row[0],
            'count': row[1]
        } for row in self.cursor.fetchall()]

        return stats


# ==================== USAGE EXAMPLES ====================


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

    # Initialize exporter
    exporter = DatabaseToJSONExporter(DB_CONFIG)

    try:
        # Connect to database
        if not exporter.connect():
            return

        # Option 1: Export with metadata
        print("\n" + "=" * 70)
        print("OPTION 1: Export with metadata")
        print("=" * 70)
        exporter.export_to_json_file(
            schema=SCHEMA,
            table=TABLE,
            output_file='claims_with_metadata.json',
            # limit=100  # Uncomment to limit rows
        )

        # Option 2: Export data only (cleaner format)
        print("\n" + "=" * 70)
        print("OPTION 2: Export data only")
        print("=" * 70)
        exporter.export_data_only(
            schema=SCHEMA,
            table=TABLE,
            output_file='claims_data.json',
            # limit=100  # Uncomment to limit rows
        )

        # Option 3: Get summary statistics
        print("\n" + "=" * 70)
        print("OPTION 3: Export with statistics")
        print("=" * 70)
        stats = exporter.get_summary_statistics(SCHEMA, TABLE)

        with open('claims_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(" Statistics saved to: claims_statistics.json")
        print("Quick Stats:")
        print(f"  Total claims: {stats['total_claims']}")
        print(
            f"  Total gross paid: SGD {stats['financial_summary']['total_gross_paid']:,.2f}"
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
    print("MSIG TRAVEL INSURANCE CLAIMS - DATABASE EXPORTER")
    print("=" * 70)
    main()
