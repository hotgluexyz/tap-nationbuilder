"""NationBuilder Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class NationBuilderAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for NationBuilder."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AutomaticTestTap API.

        Returns:
            A dict with the request body
        """
        return {
            'client_id': self.config["client_id"],
            'client_secret': self.config["client_secret"],
            'redirect_uri': self.config["redirect_uri"],
            'refresh_token': self.config["refresh_token"],
            'grant_type': 'refresh_token',
        }

    @classmethod
    def create_for_stream(cls, stream) -> "NationBuilderAuthenticator":
        """Instantiate an authenticator for a specific Singer stream.

        Args:
            stream: The Singer stream instance.

        Returns:
            A new authenticator.
        """
        return cls(
            stream=stream,
            # TODO: Customize subdomain
            auth_endpoint="https://hotglue.nationbuilder.com/oauth/token",
        )
