import logging
import uuid
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import AlvoInvestigacao
from .serializers import AlvoInvestigacaoSerializer


class AlvoInvestigacaoListCreateView(generics.ListCreateAPIView):
    queryset = AlvoInvestigacao.objects.all()
    serializer_class = AlvoInvestigacaoSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlvoInvestigacaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AlvoInvestigacao.objects.all()
    serializer_class = AlvoInvestigacaoSerializer
    permission_classes = [permissions.IsAuthenticated]


from rest_framework.views import APIView

class AlvoInvestigacaoUpdateDocumentoView(APIView):
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request, pk):
        try:
            # Get the target instance
            instance = AlvoInvestigacao.objects.get(pk=pk)
            
            # Check if the numero_identificacao field is in the request data
            if isinstance(request.data, dict):
                numero_identificacao = request.data.get('numero_identificacao')
            else:
                # If request.data is not a dict, try to parse it differently
                numero_identificacao = getattr(request.data, 'get', lambda x, default=None: default)('numero_identificacao')
            
            if numero_identificacao is None:
                return Response({'error': 'Apenas o campo numero_identificacao pode ser atualizado'}, status=400)
            
            # Check if this CPF already exists for another target
            existing_target_with_cpf = AlvoInvestigacao.objects.filter(cpf=numero_identificacao).exclude(pk=pk).first()
            if existing_target_with_cpf:
                return Response({'error': f'O Número de identidade {numero_identificacao} já está associado a outro alvo (ID: {existing_target_with_cpf.id})'}, status=400)
            
            # Update the cpf field (numero_identificacao maps to cpf in the model)
            instance.cpf = numero_identificacao
            instance.save(update_fields=['cpf'])
            
            # Return the updated instance
            serializer = AlvoInvestigacaoSerializer(instance)
            return Response(serializer.data)
        
        except AlvoInvestigacao.DoesNotExist:
            return Response({'error': 'Target not found'}, status=404)
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.exception(f"Error updating target {pk}: {str(e)}")
            return Response({'error': str(e)}, status=500)


from informacoes_suspeitas.models import InformacaoSuspeita
from facial_recognition.models import Suspect

class AddSuspectAsTargetView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Get the suspect ID from the request data
            suspect_id = request.data.get('suspect_id')
            
            if not suspect_id:
                return Response({'error': 'Suspect ID is required'}, status=400)
            
            # Get the suspect from informacoes_suspeitas app
            try:
                informacao_suspeita = InformacaoSuspeita.objects.get(id=suspect_id)
                suspect = informacao_suspeita.suspect
                
                # Check if suspect exists
                if not suspect:
                    return Response({'error': 'Suspect not associated with this information'}, status=400)
                    
            except InformacaoSuspeita.DoesNotExist:
                return Response({'error': 'Suspect information not found'}, status=404)
            except AttributeError:
                return Response({'error': 'Suspect not associated with this information'}, status=400)
            
            # Create a new investigation target based on the suspect
            # Only map fields that exist in the Suspect model
            full_name = getattr(suspect, 'full_name', 'Nome Desconhecido')
            suspect_nid = getattr(suspect, 'nid', '') or ''
            
            alvo_data = {
                'nome': full_name,
                'apelido': getattr(suspect, 'nickname', '') or '',
                'cpf': suspect_nid,  # Use NID field from suspect model
                'endereco': '',  # Suspect model doesn't have address field
                'telefone': '',  # Suspect model doesn't have phone field
                'email': '',  # Suspect model doesn't have email field
                'investigador_responsavel': request.user.id if request.user.is_authenticated else None,
                'observacoes': f'Adicionado a partir de informacao suspeita ID: {informacao_suspeita.id}',
                'status': 'ativo',  # Default status
            }
            
            # If no NID was provided, generate a default one to satisfy unique constraint
            if not suspect_nid:
                import uuid
                alvo_data['cpf'] = f"DEFAULT_{str(uuid.uuid4())[:8]}"
            
            # Map dangerous_level to nivel_prioridade if it exists
            if getattr(suspect, 'dangerous_level', None):
                # Map the dangerous level to priority level
                dangerous_level = getattr(suspect, 'dangerous_level', '').lower()
                if 'alta' in dangerous_level or 'high' in dangerous_level:
                    alvo_data['nivel_prioridade'] = 5
                elif 'media' in dangerous_level or 'medium' in dangerous_level:
                    alvo_data['nivel_prioridade'] = 3
                elif 'baixa' in dangerous_level or 'low' in dangerous_level:
                    alvo_data['nivel_prioridade'] = 1
            else:
                alvo_data['nivel_prioridade'] = 1  # Default priority level
            
            # Create the new target
            serializer = AlvoInvestigacaoSerializer(data=alvo_data)
            if serializer.is_valid():
                target = serializer.save()
                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)
                
        except Exception as e:
            logging.exception(f"Error adding suspect as target: {str(e)}")
            return Response({'error': str(e)}, status=500)
