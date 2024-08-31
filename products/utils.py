import csv

import numpy as np
import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import HttpResponse

from .models import Product
from .validators import FileValidator
from .constants import REQUIRED_COLUMNS


class CleanAndUploadProductUtils:
    @staticmethod
    def process_csv_file(file):
        """
        Reads and processes the CSV file.

        :param file: The uploaded CSV file.
        :return: A DataFrame containing the processed data.
        :raises ValidationError: If the file is empty, cannot be read, or has parsing issues.
        """
        try:
            # Attempt to read the uploaded CSV file into a pandas DataFrame.
            df = pd.read_csv(file)
        except pd.errors.EmptyDataError:
            # Raise an error if the CSV file is empty.
            raise ValidationError("The file is empty or cannot be read.")
        except pd.errors.ParserError:
            # Raise an error if there's an issue parsing the CSV file.
            raise ValidationError("Error parsing the CSV file.")

        # Validate the DataFrame to ensure it contains all required columns.
        FileValidator.validate_columns(df, REQUIRED_COLUMNS)

        return df

    @staticmethod
    def clean_product_data(df):
        """
        Cleans the product data by filling in missing values.

        :param df: The DataFrame containing product data.
        :return: The cleaned DataFrame.
        """
        # Fill missing values in the 'price' column with the median value.
        df['price'].fillna(df['price'].median(), inplace=True)

        # Fill missing values in the 'quantity_sold' column with the median value.
        df['quantity_sold'].fillna(df['quantity_sold'].median(), inplace=True)

        # Fill missing values in the 'rating' column with the mean rating within each category.
        overall_mean = df['rating'].mean()

        # Fill NaN values in the 'rating' column based on the category mean or overall mean
        df['rating'] = df.groupby('category')['rating'].transform(
            lambda x: x.fillna(x.mean() if not np.isnan(x.mean()) else overall_mean)
        )

        return df

    @staticmethod
    def save_products_to_db(df, operation_type):
        """
        Saves the products from the DataFrame to the database.

        :param df: The DataFrame containing product data.
        :param operation_type: The operation type ('append' or other). If not 'append', existing data will be cleared.
        """
        if operation_type != "true":
            # Clear existing product data if the operation type is not 'append'.
            Product.objects.all().delete()

        try:
            with transaction.atomic():
                # Iterate over each row in the DataFrame and update or create the product in the database.
                for index, row in df.iterrows():
                    Product.objects.update_or_create(
                        product_id=row['product_id'],
                        defaults={
                            'product_name': row['product_name'],
                            'category': row['category'],
                            'price': row['price'],
                            'quantity_sold': row['quantity_sold'],
                            'rating': row['rating'],
                            'review_count': row['review_count']
                        }
                    )
        except Exception as e:
            raise ValidationError(f"Exception is {str(e)} in row {index + 2}")


class SummaryReportUtils:
    @staticmethod
    def generate_summary_report(products):
        """
        Generates a summary report from the given products queryset.

        :param products: Queryset of Product objects.
        :return: A CSV HttpResponse containing the summary report.
        """
        # Convert the queryset of Product objects to a pandas DataFrame.
        df = pd.DataFrame(list(products.values()))

        # Aggregate data to create the summary, grouped by 'category'.
        summary = df.groupby('category').agg(
            total_revenue=pd.NamedAgg(column='price', aggfunc='sum'),
            top_product=pd.NamedAgg(column='product_name', aggfunc=lambda x: x.iloc[0]),
            top_product_quantity_sold=pd.NamedAgg(column='quantity_sold', aggfunc='max')
        ).reset_index()

        # Prepare the CSV response to be sent back to the client.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

        # Write the summary data into the CSV response.
        writer = csv.writer(response)
        writer.writerow(summary.columns)  # Write CSV headers
        for row in summary.itertuples(index=False):
            writer.writerow(row)

        return response


def validate_non_negative(self, value, field_name):
    """
    Validates that the given value is non-negative.

    :param value: The value to validate.
    :param field_name: The name of the field being validated.
    :raises ValueError: If the value is negative.
    """
    if value is not None and value < 0:
        # Raise an error if the value is negative.
        raise ValidationError(
            f"{field_name.replace('_', ' ').capitalize()} cannot be negative.")
