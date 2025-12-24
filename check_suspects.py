#!/usr/bin/env python3
"""
Simple script to check if there are suspects in the database.
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacip_backend.settings')
django.setup()

# Import Django models after setting up Django
from facial_recognition.models import Suspect

def main():
    """Check suspects in database."""
    print("Checking suspects in database...")
    
    # Count suspects
    suspect_count = Suspect.objects.count()
    print(f"Total suspects in database: {suspect_count}")
    
    if suspect_count > 0:
        # Show first few suspects
        suspects = Suspect.objects.all()[:5]
        print("\nFirst 5 suspects:")
        for suspect in suspects:
            print(f"- ID: {suspect.id}, Name: {suspect.full_name}, Nickname: {suspect.nickname}")
            
            # Check if they have embeddings
            embeddings = suspect.get_embeddings()
            if embeddings:
                print(f"  Has embeddings: Yes, count: {len(embeddings)}")
            else:
                print(f"  Has embeddings: No")
    else:
        print("No suspects found in database.")
        print("Please run the populate script to add suspects:")
        print("  python manage.py update_suspects_from_api")

if __name__ == "__main__":
    main()