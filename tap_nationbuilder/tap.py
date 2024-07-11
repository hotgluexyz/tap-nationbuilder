"""NationBuilder tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_nationbuilder import streams


class TapNationBuilder(Tap):
    """NationBuilder tap class."""

    name = "tap-nationbuilder"

    def __init__(
        self,
        config=None,
        catalog=None,
        state=None,
        parse_env_config=False,
        validate_config=True,
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, catalog, state, parse_env_config, validate_config)

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.NationBuilderStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ContactsStream(self),
        ]


if __name__ == "__main__":
    TapNationBuilder.cli()
