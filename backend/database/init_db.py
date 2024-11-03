import json
import os
from chromadb_manager import ChromaDBManager

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def init_database():
    # Get the absolute path to the data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    chroma_dir = os.path.join(data_dir, 'chromadb')
    
    # Create ChromaDB manager
    db_manager = ChromaDBManager(chroma_dir)
    
    # Load and insert health tips
    tips_data = load_json_data(os.path.join(data_dir, 'health_knowledge', 'health_tips.json'))
    for tip in tips_data['tips']:
        db_manager.add_health_tip(
            tip_id=tip['id'],
            tip_text=tip['text'],
            category=tip['category']
        )
    
    # Load and insert FAQs
    faqs_data = load_json_data(os.path.join(data_dir, 'health_knowledge', 'faqs.json'))
    for faq in faqs_data['faqs']:
        db_manager.add_faq(
            faq_id=faq['id'],
            question=faq['question'],
            answer=faq['answer'],
            category=faq['category']
        )
    
    # Load and insert products
    products_data = load_json_data(os.path.join(data_dir, 'health_knowledge', 'products.json'))
    for product in products_data['products']:
        db_manager.add_product(
            product_id=product['id'],
            name=product['name'],
            description=product['description'],
            category=product['category'],
            price=product['price']
        )

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")