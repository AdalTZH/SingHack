"""
Taxonomy Data Loader
Loads and provides access to the insurance taxonomy JSON data
"""
import json
import os
from typing import Dict, List, Optional, Any
from .config import TAXONOMY_JSON_PATH
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxonomyLoader:
    """
    Loader for insurance taxonomy JSON data
    Provides methods to query benefit, condition, and product information
    """
    
    def __init__(self, json_path: Optional[str] = None):
        """
        Initialize the taxonomy loader
        
        Args:
            json_path: Path to the taxonomy JSON file. If None, uses default from config.
        """
        self.json_path = json_path or TAXONOMY_JSON_PATH
        self.taxonomy_data = None
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """Load taxonomy data from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.taxonomy_data = json.load(f)
            logger.info(f"Loaded taxonomy data from {self.json_path}")
        except FileNotFoundError:
            logger.error(f"Taxonomy file not found: {self.json_path}")
            self.taxonomy_data = None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing taxonomy JSON: {e}")
            self.taxonomy_data = None
    
    def get_benefit_by_name(self, benefit_name: str, layer: str = 'layer_2_benefits') -> Optional[Dict[str, Any]]:
        """
        Get benefit information by benefit name
        
        Args:
            benefit_name: Name of the benefit to retrieve
            layer: Layer name (default: layer_2_benefits)
            
        Returns:
            Benefit data dictionary or None if not found
        """
        if not self.taxonomy_data:
            return None
        
        layers = self.taxonomy_data.get('layers', {})
        layer_data = layers.get(layer, [])
        
        for benefit in layer_data:
            if benefit.get('benefit_name') == benefit_name:
                return benefit
        
        return None
    
    def get_condition_by_name(self, condition_name: str, layer: str = 'layer_1_general_conditions') -> Optional[Dict[str, Any]]:
        """
        Get condition information by condition name
        
        Args:
            condition_name: Name of the condition to retrieve
            layer: Layer name (default: layer_1_general_conditions)
            
        Returns:
            Condition data dictionary or None if not found
        """
        if not self.taxonomy_data:
            return None
        
        layers = self.taxonomy_data.get('layers', {})
        layer_data = layers.get(layer, [])
        
        for condition in layer_data:
            if condition.get('condition') == condition_name:
                return condition
        
        return None
    
    def get_benefit_names(self, layer: str = 'layer_2_benefits') -> List[str]:
        """
        Get all benefit names from a layer
        
        Args:
            layer: Layer name
            
        Returns:
            List of benefit names
        """
        if not self.taxonomy_data:
            return []
        
        layers = self.taxonomy_data.get('layers', {})
        layer_data = layers.get(layer, [])
        
        return [item.get('benefit_name') or item.get('condition') for item in layer_data if item.get('benefit_name') or item.get('condition')]
    
    def search_benefits(self, search_term: str, layer: str = 'layer_2_benefits') -> List[Dict[str, Any]]:
        """
        Search for benefits matching a search term
        
        Args:
            search_term: Term to search for
            layer: Layer name
            
        Returns:
            List of matching benefit dictionaries
        """
        if not self.taxonomy_data:
            return []
        
        layers = self.taxonomy_data.get('layers', {})
        layer_data = layers.get(layer, [])
        
        search_term_lower = search_term.lower()
        matches = []
        
        for item in layer_data:
            # Search in benefit name or condition name
            item_name = item.get('benefit_name') or item.get('condition', '')
            if search_term_lower in item_name.lower():
                matches.append(item)
        
        return matches
    
    def get_product_info(self, product_name: str, benefit_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get product information for a specific benefit or all benefits
        
        Args:
            product_name: Name of the product (e.g., 'Product A', 'Product B', 'Product C')
            benefit_name: Optional benefit name to filter by
            
        Returns:
            Product information dictionary or None if not found
        """
        if not self.taxonomy_data:
            return None
        
        if benefit_name:
            benefit = self.get_benefit_by_name(benefit_name)
            if benefit:
                return benefit.get('products', {}).get(product_name)
        else:
            # Return all product information across all benefits
            all_product_info = {}
            for layer_name, layer_data in self.taxonomy_data.get('layers', {}).items():
                for item in layer_data:
                    item_name = item.get('benefit_name') or item.get('condition', '')
                    products = item.get('products', {})
                    if product_name in products:
                        if item_name not in all_product_info:
                            all_product_info[item_name] = {}
                        all_product_info[item_name] = products[product_name]
            return all_product_info
        
        return None
    
    def get_all_products(self) -> List[str]:
        """
        Get list of all products in taxonomy
        
        Returns:
            List of product names
        """
        if not self.taxonomy_data:
            return []
        
        return self.taxonomy_data.get('products', [])
    
    def get_taxonomy_structure(self) -> Dict[str, Any]:
        """
        Get the overall taxonomy structure
        
        Returns:
            Dictionary with taxonomy metadata
        """
        if not self.taxonomy_data:
            return {}
        
        return {
            'name': self.taxonomy_data.get('taxonomy_name', ''),
            'products': self.taxonomy_data.get('products', []),
            'layers': list(self.taxonomy_data.get('layers', {}).keys())
        }


# Global instance for easy access
_taxonomy_loader_instance = None


def get_taxonomy_loader() -> TaxonomyLoader:
    """Get or create global taxonomy loader instance"""
    global _taxonomy_loader_instance
    if _taxonomy_loader_instance is None:
        _taxonomy_loader_instance = TaxonomyLoader()
    return _taxonomy_loader_instance

