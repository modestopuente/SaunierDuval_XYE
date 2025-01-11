'''Saunier Duval Fancoil XYE'''
import asyncio
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .xye import xye

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["climate"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the XYE component."""

    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up XYE from a config entry."""
    xye_host = entry.data["xye_host"]
    xye_port = entry.data["xye_port"]
    xye_target = entry.data["xye_target"]    
    xye_source = entry.data["xye_source"]
    xye_scaninterval = entry.data["scan_interval"]
    xye_alias = entry.data["alias"]

    xyeApi = xye(xye_host, xye_port, xye_target, xye_source)


    '''
    # Fetch initial data so we have data when entities subscribe
    coordinator = XYECoordinator(
        hass, xyeApi, xye_alias, xye_scaninterval
    )
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = HassXYE(
        coordinator, xye_host, xye_port, xye_target, xye_source
    )
    '''
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class HassXYE:
    def __init__(
        self, coordinator: DataUpdateCoordinator, xye_host: str, xye_port: int, xye_target: int, xye_source: int
    ):
        self._xye_host = xye_host
        self._xye_port = xye_port
        self._xye_target = xye_target
        self._xye_source = xye_source
        _LOGGER.debug("XYE __init__" + self._xye_host)

        # create an instance of XYEConnector
        self._coordinator = coordinator

    def get_name(self):
        return f"xye_{self._xye_host}_{str(self._xye_target)}"

    def get_unique_id(self):
        return f"xye_{self._xye_host}_{str(self._xye_target)}"


class XYECoordinator(DataUpdateCoordinator):
    """XYE coordinator."""

    def __init__(self, hass, xyeAPI: xye, alias: str, pollinterval: int):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"XYE coordinator for '{alias}'",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=pollinterval),
        )
        self.xyeApi = xyeAPI
        self._alias = alias


    '''
    async def _async_update_data(self):
        # Fetch data from API endpoint. This is the place to pre-process the data to lookup tables so entities can quickly look up their data.

        try:
            retData = {}
            async with asyncio.timeout(3):
                retData["power"] = self.xyeApi.GetPowerOutput()
                retData["time"] = self.xyeApi.GetInverterTime()

                return retData
        except:
            _LOGGER.error("XYECoordinator _async_update_data failed")
        # except ApiAuthError as err:
        #     # Raising ConfigEntryAuthFailed will cancel future updates
        #     # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #     raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #     raise UpdateFailed(f"Error communicating with API: {err}")
        
 '''