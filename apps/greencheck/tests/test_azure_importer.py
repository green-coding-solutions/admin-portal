import pytest
import pathlib
import json
from io import StringIO

from django.core.management import call_command
from apps.greencheck.importers.azure_importer import AzureImporter

from django.conf import settings


@pytest.fixture
def sample_data():
    """
    Retrieve a locally saved sample of the population to use for this test
    Return: JSON
    """
    this_file = pathlib.Path(__file__)
    json_path = this_file.parent.parent.joinpath("fixtures", "azure_test_sample.json")
    with open(json_path) as ipr:
        return json.loads(ipr.read())


@pytest.mark.django_db
class TestAzureImporter:
    def test_parse_to_list(self, sample_data):
        """
        Test the parsing function.
        """
        # Initialize Azure importer
        importer = AzureImporter()

        # Run parse list with sample data
        list_of_addresses = importer.parse_to_list(sample_data)

        # Test: resulting list contains items
        assert len(list_of_addresses) > 0

@pytest.mark.django_db
class TestAzureImportCommand:
    """
    This just tests that we have a management command that can run.
    We _could_ mock the call to fetch ip ranges, if this turns out to be a slow test.
    """

    def test_handle(self, mocker, sample_data):
        # mock the call to retrieve from source, to a locally stored
        # testing sample. By instead using the test sample,
        # we avoid unnecessary network requests.

        # identify method we want to mock
        path_to_mock = (
            "apps.greencheck.importers.azure_importer."
            "AzureImporter.fetch_data_from_source"
        )

        # define a different return when the targeted mock
        # method is called
        mocker.patch(
            path_to_mock, return_value=sample_data,
        )

        out = StringIO()
        call_command("update_azure_network", stdout=out)
        # TODO: Report back on the output
