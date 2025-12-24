#!/usr/bin/env python
"""
Script to create suspicious information entries and link them with facial recognition suspects.
"""

import os
import sys
import django
import numpy as np
import cv2
from pathlib import Path

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacip_backend.settings')
django.setup()

# Import Django models after setting up Django
from facial_recognition.models import Suspect
from informacoes_suspeitas.models import InformacaoSuspeita
from users.models import User

# Import InsightFace
try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("InsightFace not available. Facial recognition will be disabled.")

# Configuration
MODEL_NAME = 'buffalo_l'
MEDIA_ROOT = Path(__file__).parent.parent / 'media'

# Create media directory if it doesn't exist
MEDIA_ROOT.mkdir(exist_ok=True)

# Initialize FaceAnalysis
if INSIGHTFACE_AVAILABLE:
    face_app = FaceAnalysis(name=MODEL_NAME, providers=['CPUExecutionProvider'], root=Path("models"))
    face_app.prepare(ctx_id=0, det_size=(640, 640))
else:
    face_app = None


def create_sample_embedding():
    """Create a sample face embedding for testing."""
    # Generate a random embedding vector (512-dimensional for ArcFace)
    return np.random.rand(512).tolist()


def create_test_image(filename, text):
    """Create a simple test image with text."""
    # Create a black image
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Add text to the image
    cv2.putText(img, text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Save the image
    filepath = MEDIA_ROOT / filename
    cv2.imwrite(str(filepath), img)
    return filename


def create_test_suspects_with_info():
    """Create test suspects with sample data and link them with suspicious information."""
    if not INSIGHTFACE_AVAILABLE:
        print("InsightFace is not available. Cannot extract face embeddings.")
        return
        
    print("Creating test suspects and linking with suspicious information...")
    
    # Get or create a test user
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Test suspect data
    test_suspects = [
        {
            'full_name': 'João Silva',
            'nickname': 'Zé',
            'nid': '123456789',
            'dangerous_level': 'Alto',
            'dangerous_color': 'red',
            'info_title': 'Suspeito envolvido em roubo a banco',
            'info_description': 'Indivíduo suspeito de participar em assalto a banco na zona central da cidade.',
            'info_source': 'Relato policial',
        },
        {
            'full_name': 'Maria Santos',
            'nickname': 'Mari',
            'nid': '987654321',
            'dangerous_level': 'Médio',
            'dangerous_color': 'yellow',
            'info_title': 'Suspeita de tráfico de drogas',
            'info_description': 'Indivíduo observado em atividades suspeitas relacionadas ao tráfico de substâncias controladas.',
            'info_source': 'Inteligência policial',
        },
        {
            'full_name': 'Carlos Oliveira',
            'nickname': 'Carlão',
            'nid': '456789123',
            'dangerous_level': 'Baixo',
            'dangerous_color': 'green',
            'info_title': 'Suspeito de furto de veículos',
            'info_description': 'Indivíduo com histórico de envolvimento em roubos de automóveis usados.',
            'info_source': 'Boletim de ocorrência',
        }
    ]
    
    # Create test images and suspects
    for i, suspect_data in enumerate(test_suspects):
        try:
            # Create a test image
            image_filename = f"test_suspect_{i+1}.jpg"
            create_test_image(image_filename, suspect_data['nickname'])
            
            # Create sample embedding
            embedding = create_sample_embedding()
            
            # Save suspect to database
            suspect, created = Suspect.objects.get_or_create(
                id=i+1,
                defaults={
                    'full_name': suspect_data['full_name'],
                    'nickname': suspect_data['nickname'],
                    'nid': suspect_data['nid'],
                    'dangerous_level': suspect_data['dangerous_level'],
                    'dangerous_color': suspect_data['dangerous_color'],
                }
            )
            
            # Update suspect with photo paths and embeddings
            suspect.set_photo_paths([image_filename])
            suspect.set_embeddings([embedding])
            suspect.save()
            
            if created:
                print(f"Added new test suspect: {suspect_data['full_name']}")
            else:
                print(f"Updated existing test suspect: {suspect_data['full_name']}")
                
            # Create suspicious information linked to this suspect
            info, info_created = InformacaoSuspeita.objects.get_or_create(
                titulo=suspect_data['info_title'],
                defaults={
                    'descricao': suspect_data['info_description'],
                    'fonte': suspect_data['info_source'],
                    'nivel_confianca': 7,
                    'criado_por': user,
                    'suspect': suspect,  # Link to the facial recognition suspect
                }
            )
            
            if info_created:
                print(f"Added new suspicious information for {suspect_data['full_name']}")
            else:
                print(f"Updated existing suspicious information for {suspect_data['full_name']}")
                
        except Exception as e:
            print(f"Error creating test suspect {suspect_data.get('full_name', 'Unknown')}: {e}")
            continue
            
    print("Finished creating test suspects and linking with suspicious information.")


if __name__ == "__main__":
    create_test_suspects_with_info()