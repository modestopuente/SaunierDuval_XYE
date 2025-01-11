"""Config flow for XYE integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_ALIAS
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN,CONF_XYE_HOST,CONF_XYE_PORT,CONF_XYE_TARGET,CONF_XYE_SOURCE,CONF_XYE_POLL,DEFAULT_SCAN_INTERVAL,DEFAULT_CONF_DEVICE_ID, DEFAULT_CONF_SOURCE
"""Constants for the XYE integration."""

_LOGGER = logging.getLogger(__name__)

STEP_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_XYE_HOST, default=None): str,
        vol.Required(CONF_XYE_PORT, default=8899): int,
        vol.Required(CONF_XYE_TARGET, default=DEFAULT_CONF_DEVICE_ID): int,
        vol.Required(CONF_XYE_SOURCE, default=DEFAULT_CONF_SOURCE): str,
        vol.Optional(CONF_XYE_POLL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)
STEP_DATA_ALIAS = vol.Schema(
    {
        vol.Required(CONF_ALIAS): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for XYE."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                self._userInput = user_input
                return await self.async_step_alias()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_DATA_SCHEMA, errors=errors
        )

    async def async_step_alias(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the alias step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._userInput[CONF_ALIAS] = user_input[CONF_ALIAS]
                _LOGGER.info(user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"{self._userInput[CONF_ALIAS]}  ({self._userInput[CONF_XYE_HOST]}:{self._userInput[CONF_XYE_PORT]})_{self._userInput[CONF_XYE_TARGET]})",
                    data=self._userInput,
                )

        return self.async_show_form(
            step_id="alias", data_schema=STEP_DATA_ALIAS, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""