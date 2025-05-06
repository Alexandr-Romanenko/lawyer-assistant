from django.urls import path
from api.views import DecisionUploadView, SearchView

urlpatterns = [
    path('decision_upload/', DecisionUploadView.as_view(), name="decision_upload"),
    path("search/", SearchView.as_view(), name="search-view"),
]
