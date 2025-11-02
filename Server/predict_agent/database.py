"""
Database connection and query utilities for claims data
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Handles PostgreSQL database connections"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info("Successfully connected to database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def get_claims_by_destination(destination):
    """Get claims data filtered by destination"""
    query = """
        SELECT 
            product_name,
            product_category,
            claim_type,
            cause_of_loss,
            loss_type,
            COUNT(*) as claim_count,
            AVG(gross_incurred) as avg_claim_amount,
            SUM(gross_incurred) as total_claims,
            SUM(CASE WHEN claim_status = 'Closed' THEN 1 ELSE 0 END) as closed_claims,
            SUM(CASE WHEN claim_status = 'Open' THEN 1 ELSE 0 END) as open_claims
        FROM hackathon.claims
        WHERE LOWER(destination) LIKE LOWER(%s)
        GROUP BY product_name, product_category, claim_type, cause_of_loss, loss_type
        ORDER BY claim_count DESC
    """
    return query, [f'%{destination}%']


def get_claims_by_claim_type(claim_type):
    """Get claims data filtered by claim type"""
    query = """
        SELECT 
            product_name,
            product_category,
            COUNT(*) as claim_count,
            AVG(gross_incurred) as avg_claim_amount,
            SUM(gross_incurred) as total_claims,
            AVG(CASE WHEN closed_date IS NOT NULL THEN closed_date - report_date ELSE NULL END) as avg_processing_days
        FROM hackathon.claims
        WHERE LOWER(claim_type) LIKE LOWER(%s)
        GROUP BY product_name, product_category
        ORDER BY claim_count DESC
    """
    return query, [f'%{claim_type}%']


def get_product_performance_stats():
    """Get overall performance statistics for each product"""
    query = """
        SELECT 
            product_name,
            product_category,
            COUNT(*) as total_claims,
            COUNT(DISTINCT destination) as unique_destinations,
            AVG(gross_incurred) as avg_claim_amount,
            SUM(gross_incurred) as total_claim_amount,
            SUM(CASE WHEN claim_status = 'Closed' THEN gross_paid ELSE 0 END) as total_paid,
            COUNT(DISTINCT claim_type) as claim_type_diversity,
            COUNT(DISTINCT loss_type) as loss_type_diversity,
            AVG(CASE WHEN closed_date IS NOT NULL THEN closed_date - report_date ELSE NULL END) as avg_processing_days
        FROM hackathon.claims
        GROUP BY product_name, product_category
        ORDER BY total_claims DESC
    """
    return query, None


def get_recent_claims(limit=100):
    """Get recent claims for trend analysis"""
    query = """
        SELECT 
            product_name,
            destination,
            claim_type,
            cause_of_loss,
            loss_type,
            accident_date,
            gross_incurred,
            claim_status
        FROM hackathon.claims
        ORDER BY accident_date DESC
        LIMIT %s
    """
    return query, [limit]

