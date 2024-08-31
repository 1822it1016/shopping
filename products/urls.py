from django.contrib import admin
from django.urls import path

from .views import CleanAndUploadProductView, ProductListView, SummaryReportView

urlpatterns = [
    path("upload-file", CleanAndUploadProductView.as_view()),
    path("product", ProductListView.as_view()),
    path("report", SummaryReportView.as_view())
]
