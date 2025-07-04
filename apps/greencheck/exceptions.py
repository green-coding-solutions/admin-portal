from rest_framework.exceptions import NotFound


class NoSharedSecret(NotFound):
    """
    An exception raised when we try to fetch a shared secret for a provider
    but no shared secret has been set.
    """

    default_detail = "No shared secret is set. Create one by sending an empty POST request to this endpoint"
    default_code = "no_shared_secret"


class ImportingForArchivedProvider(Exception):
    """
    An exception raised when we try to import data for a provider
    that has been archived.
    """

    default_detail = (
        "This provider has been archived. Please unarchive it before importing data."
    )
    default_code = "archived_provider"
