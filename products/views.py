from .models import Product
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from .utils import CleanAndUploadProductUtils, SummaryReportUtils
from .validators import FileValidator


class ProductListView(APIView):
    def get(self, request):
        """
        Handles GET requests to retrieve all products from the database.

        :param request: The request object.
        :return: A Response containing the serialized product data.
        """
        # Retrieve all products from the database.
        products = Product.objects.all()

        # Serialize the queryset of products.
        serializer = ProductSerializer(products, many=True)

        # Return the serialized data in the response.
        return Response(serializer.data)

    def post(self, request):
        """
        Handles POST requests to create a new product entry in the Product table.

        :param request: The request object containing product data.
        :return: A Response indicating success or failure.
        """
        # Deserialize the incoming product data.
        serializer = ProductSerializer(data=request.data)

        # Validate and save the product if the data is valid.
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors if the data is invalid.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CleanAndUploadProductView(APIView):
    """
    API view to handle the uploading and processing of product data from a CSV file.
    """

    def post(self, request):
        """
        Handles POST requests to upload and process a CSV file.

        The method validates the file, processes and cleans the data, and updates or creates Product instances in the database.

        :param request: The request object containing the uploaded file and operation type.
        :return: A Response object indicating success or failure.
        """
        # Retrieve the uploaded file from the request.
        file = request.FILES.get('file')

        # Get the value of the 'append' query parameter.
        operation_type = request.query_params.get('append')

        try:
            # Validate the uploaded file.
            FileValidator.validate_file(file)

            # Process the CSV file into a DataFrame.
            df = CleanAndUploadProductUtils.process_csv_file(file)

            # Clean the product data in the DataFrame.
            df = CleanAndUploadProductUtils.clean_product_data(df)

            # Save the cleaned data to the database.
            CleanAndUploadProductUtils.save_products_to_db(df, operation_type)

            # Return a success response if everything is processed correctly.
            return Response({"success": "Products processed and uploaded successfully"}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            # Return a 400 error if there's a validation issue with the file or data.
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Return a 500 error for any unexpected issues.
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SummaryReportView(APIView):
    """
    API view to generate a summary report of all the products stored in the database.
    """

    def get(self, request):
        """
        Handles GET requests to generate the summary report.

        :param request: The request object.
        :return: A CSV HttpResponse containing the summary report or an error message.
        """
        # Retrieve all products from the database.
        products = Product.objects.all()

        # Check if there are any products available.
        if not products.exists():
            return Response({"error": "No products available for generating the summary."}, status=404)

        # Generate the summary report using the utility function and return it.
        return SummaryReportUtils.generate_summary_report(products)
