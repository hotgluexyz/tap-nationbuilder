"""NationBuilder Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from datetime import datetime
from singer_sdk.helpers._util import utc_now
import requests
import json

# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class NationBuilderAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for NationBuilder."""

    def __init__(
        self,
        stream,
        auth_endpoint: str | None = None,
        oauth_scopes: str | None = None,
        default_expiration: int | None = None,
    ) -> None:
        super().__init__(stream=stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes, default_expiration=default_expiration)
        self._tap = stream._tap


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

    # Authentication and refresh
    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload
        token_response = requests.post(
            self.auth_endpoint,
            data=auth_request_payload,
            timeout=60,
        )
        try:
            token_response.raise_for_status()
        except requests.HTTPError as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}",
            ) from ex

        self.logger.info("OAuth authorization attempt was successful.")

        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json.get("expires_in", self._default_expiration)
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires.",
            )
        self.last_refreshed = request_time
        # Log the refresh_token
        self.logger.info(f"Latest refresh token: {token_json['refresh_token']}")

        self._tap._config["access_token"] = token_json["access_token"]
        self._tap._config["refresh_token"] = token_json["refresh_token"]
        self._tap._config["expires_in"] = self.expires_in

        with open(self._tap.config_file, "w") as outfile:
            json.dump(self._tap._config, outfile, indent=4)
