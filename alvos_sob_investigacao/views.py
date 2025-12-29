import logging
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