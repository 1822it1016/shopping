from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Product
from .views import CleanAndUploadProductView, SummaryReportView
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response


class ProductViewsTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('products.views.FileValidator.validate_file')
    @patch('products.views.CleanAndUploadProductUtils.process_csv_file')
    @patch('products.views.CleanAndUploadProductUtils.clean_product_data')
    @patch('products.views.CleanAndUploadProductUtils.save_products_to_db')
    def test_clean_and_upload_product_view(self, mock_save_products, mock_clean_data, mock_process_file,
                                           mock_validate_file):
        mock_file = InMemoryUploadedFile(
            file=MagicMock(),
            field_name='file',
            name='test.csv',
            content_type='text/csv',
            size=1024,
            charset=None
        )
        mock_validate_file.return_value = None
        mock_process_file.return_value = MagicMock()
        mock_clean_data.return_value = MagicMock()

        url = '/upload-file'  # Direct endpoint path
        request = self.factory.post(url, {'file': mock_file}, format='multipart')

        # Act
        view = CleanAndUploadProductView.as_view()  # Instantiate the view
        response = view(request)

        # Assert
        mock_validate_file.assert_called_once()  # Use assert_called_once() to check if it was called
        actual_file = mock_validate_file.call_args[0][0]  # Get the actual argument passed
        self.assertEqual(actual_file.name, 'test.csv')
        self.assertEqual(actual_file.content_type, 'text/csv')
        mock_process_file.assert_called_once()
        mock_clean_data.assert_called_once()
        mock_save_products.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"success": "Products processed and uploaded successfully"})

    @patch('products.views.SummaryReportUtils.generate_summary_report')
    def test_summary_report_view(self, mock_generate_report):
        # Arrange
        mock_response = Response({'some': 'data'}, status=status.HTTP_200_OK)
        mock_generate_report.return_value = mock_response
        Product.objects.create(
            product_id="product_id1",
            product_name="Product A",
            category="Category 1",
            price=100,
            quantity_sold=10,
            rating=4.5,
            review_count=20
        )

        url = '/report'
        request = self.factory.get(url)

        # Act
        view = SummaryReportView.as_view()  # Instantiate the view
        response = view(request)

        # Assert
        mock_generate_report.assert_called_once()
        self.assertEqual(response.status_code, mock_response.status_code)
        self.assertEqual(response.data, mock_response.data)

    def test_summary_report_view_no_products(self):
        url = '/report'
        request = self.factory.get(url)

        view = SummaryReportView.as_view()  # Instantiate the view
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No products available for generating the summary."})
