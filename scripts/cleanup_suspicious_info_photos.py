import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacip_backend.settings')
django.setup()

from informacoes_suspeitas.models import InformacaoSuspeita

def cleanup_photos():
    """
    Remove photo references from all suspicious information records in the database
    This will allow them to be re-downloaded during the next sync
    """
    print("Cleaning up photo references from suspicious information records...")
    
    # Get all records that have a photo field set
    records_with_photos = InformacaoSuspeita.objects.exclude(photo__isnull=True).exclude(photo='')
    
    print(f"Found {records_with_photos.count()} records with photo references")
    
    for record in records_with_photos:
        print(f"Removing photo reference for: {record.titulo}")
        # Remove the photo reference from the database
        record.photo = None
        record.save()
    
    print("Cleanup completed. All photo references have been removed from the database.")
    print("Run the sync script again to re-download all images.")

if __name__ == "__main__":
    cleanup_photos()