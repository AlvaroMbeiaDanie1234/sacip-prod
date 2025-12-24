import requests
import logging
from typing import Dict, Optional, Any

# Set up logging
logger = logging.getLogger(__name__)

# External API URL for taxpayer verification
TAXPAYER_API_URL = 'https://invoice.minfin.gov.ao/commonServer/common/taxpayer/get'

def get_taxpayer_info(nif: str) -> Optional[Dict[str, Any]]:
    """
    Fetch taxpayer information from MINFIN API
    
    Args:
        nif (str): Taxpayer identification number
        
    Returns:
        dict: Taxpayer information or None if error occurs
    """
    try:
        # Make request to taxpayer API
        api_url = f"{TAXPAYER_API_URL}/{nif}"
        logger.info(f"Consultando API de contribuintes: {api_url}")
        
        api_response = requests.get(api_url, timeout=30)
        
        # Log the response for debugging
        logger.info(f"Resposta da API de contribuintes - Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            response_data = api_response.json()
            
            # Check if the response indicates success
            if response_data.get('success', False) and 'data' in response_data:
                return response_data['data']
            else:
                logger.warning(f"API de contribuintes retornou sucesso=False ou dados ausentes para NIF: {nif}")
                return None
        else:
            # Handle non-200 responses
            logger.error(f"Erro na API de contribuintes: {api_response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error('Timeout ao consultar API de contribuintes')
        return None
    except requests.exceptions.ConnectionError:
        logger.error('Erro de conexão ao consultar API de contribuintes')
        return None
    except Exception as e:
        logger.error(f'Erro ao consultar API de contribuintes: {str(e)}')
        return None