from django.urls import path
from .views import AlvoInvestigacaoListCreateView, AlvoInvestigacaoRetrieveUpdateDestroyView, AlvoInvestigacaoUpdateDocumentoView, AddSuspectAsTargetView

urlpatterns = [
    path('alvos-sob-investigacao/', AlvoInvestigacaoListCreateView.as_view(), name='alvo-investigacao-list-create'),
    path('alvos-sob-investigacao/<int:pk>/', AlvoInvestigacaoRetrieveUpdateDestroyView.as_view(), name='alvo-investigacao-detail'),
    path('alvos-sob-investigacao/<int:pk>/update-documento/', AlvoInvestigacaoUpdateDocumentoView.as_view(), name='alvo-investigacao-update-documento'),
    path('alvos-sob-investigacao/add-suspect/', AddSuspectAsTargetView.as_view(), name='add-suspect-as-target'),
]