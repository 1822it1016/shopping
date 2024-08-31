from django.core.exceptions import ValidationError
from django.conf import settings

"""
This module contains validation classes for handling file and data validations.
"""


class FileValidator:
    """
    A class to perform validation checks on files uploaded to the server.
    """

    @staticmethod
    def validate_file(file):
        """
        Validates the uploaded file for presence, size, and type.

        :param file: The file to validate.
        :raises ValidationError: If the file is missing, exceeds the maximum allowed size, or is not a CSV file.
        """
        # validate whether the file is provided in API
        if not file:
            raise ValidationError("No file provided")
        # validate the maximum size of the file
        if file.size > settings.MAX_FILE_SIZE:
            raise ValidationError(f"File size cannot be more than 5 MB. Size provided is {file.size / 1000000} MB")
        # validate the type of file provided
        if not file.name.endswith('.csv'):
            raise ValidationError("Invalid file type. Please upload a CSV file.")

    @staticmethod
    def validate_columns(chunk, required_columns):
        """
        Validates that the required columns are present in the CSV file.

        :param chunk: The DataFrame chunk to validate.
        :param required_columns: List of required columns that must be present in the DataFrame.
        :raises ValidationError: If the DataFrame is missing one or more required columns.
        """
        if not all(col in chunk.columns for col in required_columns):
            raise ValidationError(
                f"CSV file is missing one or more required columns. Mandatory columns are {required_columns}")
