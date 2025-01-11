from __future__ import annotations
import attr
import abc
import logging
from typing import Any, Mapping

from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
    FAN_AUTO,
    FAN_LOW, 
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_OFF,
    SWING_OFF,
    SWING_ON,
    ClimateEntityFeature
)


from homeassistant.components.climate import ClimateEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from .const import (
    DOMAIN,
    MIN_TARGET_TEMP,
    MAX_TARGET_TEMP,
    TARGET_TEMP_STEP,
    xye_const,
    xye_mode,
    xye_fan_speed,
    mode_flag,
    oper_flag,
    DEFAULT_CONF_DEVICE_ID,
    DEFAULT_CONF_SOURCE
)
from .xye import xye

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry

xye_host = ConfigEntry.data["xye_host"]
xye_port = ConfigEntry.data["xye_port"]
xye_target = ConfigEntry.data["xye_target"]    
xye_source = ConfigEntry.data["xye_source"]
xye_scaninterval = ConfigEntry.data["scan_interval"]
xye_alias = ConfigEntry.data["alias"]

fancoil= xye(xye_host, xye_port, xye_target, xye_source)
SCAN_INTERVAL = timedelta(seconds=xye_scaninterval)

#async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
#   async_add_entities([FanCoilClimateEntity()])
def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    add_entities([FanCoilClimateEntity()])
    
class FanCoilClimateEntity(ClimateEntity):
    '''
    _XYE_TO_HA: dict[Mode, list] = {
        #hvac_mode.AUTO: HVACMode.AUTO,
        xye_mode.OFF:  HVACMode.OFF, 
        xye_mode.COOL: HVACMode.COOL, 
        xye_mode.FAN:  HVACMode.FAN_ONLY,
        xye_mode.HEAT: HVACMode.HEAT,
    }
    '''
    _HA_MODE_TO_XYE = {
        #HVACMode.AUTO: xye_mode.AUTO,
        HVACMode.OFF: xye_mode.OFF,
        HVACMode.COOL: xye_mode.COOL,
        HVACMode.FAN_ONLY: xye_mode.FAN,
        HVACMode.HEAT: xye_mode.HEAT
    } 

    _HA_FAN_TO_XYE = {
        FAN_AUTO: xye_fan_speed.AUTO,
        FAN_HIGH: xye_fan_speed.HIGH,
        FAN_MEDIUM: xye_fan_speed.MEDIUM,
        FAN_LOW: xye_fan_speed.LOW,
        FAN_OFF: 0
    }
    _HA_SWING_TO_XYE = {
        SWING_OFF: mode_flag.NORM,
        SWING_ON:  mode_flag.SWING,
        }

    """ revisar esto"""
    #SCAN_INTERVAL = timedelta(seconds=5)

    def __init__(self):
        self._supported_hvac = list(FanCoilClimateEntity._HA_MODE_TO_XYE.keys())
        self._supported_fan_modes = list(FanCoilClimateEntity._HA_FAN_TO_XYE.keys())
        self._supported_swing_modes = list(FanCoilClimateEntity._HA_SWING_TO_XYE.keys())
        self._supported_preset_modes = ['fan','run','off','idle']
        
        self.current_target_temp = None
        self.current_temp = None
        self.payload = xye_const.PAYLOAD
        self.current_hvac_mode = None
        self.current_swing_mode = None
        self.current_run_status = None
        self.current_fan_speed = None              
    
        self.request_fan_speed = None
        
        if self.current_temp == None:
            xye.conecta(fancoil)
        
    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        #return self.component.name if self.component else None
        return "fancoil" + "_" + xye_target
    
    @property
    def should_poll(self) -> bool: 
        return True
  
    @property
    def scan_interval(self):
        """Return the unique id.""" 
        return SCAN_INTERVAL
    
    @property
    def is_aux_heat(self) -> bool | None:
        """Return true if aux heater."""
        return False

    @property
    def active_mode(self):
        return self.current_target_temp,self.current_hvac_mode,self.current_run_status
        
    @property
    def hvac_mode(self) -> str:
        """Get the hvac mode based on multimatic mode."""
        #return xye.get_hvac_mode(fancoil)
        return self.current_hvac_mode
      
    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available hvac operation modes."""
        return self._supported_hvac
    
    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.PRESET_MODE 

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        #return xye.get_current_temp(fancoil)
        return self.current_temp

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TARGET_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TARGET_TEMP

    @property
    def target_temperature_step(self):
        return TARGET_TEMP_STEP

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        #return xye.get_target_temp(fancoil)
        return self.current_target_temp

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        return self.current_fan_speed

    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available fan modes."""
        return self._supported_fan_modes

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires SUPPORT_PRESET_MODE.
        """
        return self.current_run_status

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of available preset modes.

        Requires SUPPORT_PRESET_MODE.
        """
        return self._supported_preset_modes
    
    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting."""
        #return xye.get_swing_mode(fancoil)
        return self.current_swing_mode
    
    @property
    def swing_modes(self) -> list[str]:
        return self._supported_swing_modes
        
    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _r=xye.set_hvac_mode(fancoil,self.payload, hvac_mode)
        self._parserespuesta(_r)
    
    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        _r=xye.set_fan_mode(fancoil,self.payload,fan_mode)
        self._parserespuesta(_r)
        
    def set_swing_mode(self, swing_mode):
        """Set new target swing operation."""
        _r=xye.set_swing_mode(fancoil,self.payload,swing_mode)
        self._parserespuesta(_r)
         
    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp and temp != self.current_target_temp:
            #_LOGGER.debug("Setting target temp to %s", temp)
            #await xye.set_target_temp(fancoil,temp)
            _r = xye.set_target_temp(fancoil,self.payload,temp)
            self._parserespuesta(_r)
        '''
        else:
            _LOGGER.debug("Nothing to do")
        '''   
            
    def _parserespuesta(self,r):       
        if r:
            #if r[1]==xye_const.PREAMBLE and r[31]==xye_const.PROLOGUE :
            _current_mode = r[9]
            _current_fan_speed = r[10]
            self.current_target_temp = r[11]
            self.current_temp = (r[12]-xye_const.OFFSET)/2     # T1 Temp	in 0.5 °C - 0x30
            _current_water_temp = (r[13]-xye_const.OFFSET)/2    # T2A Temp	in 0.5 °C - 0x30
            _current_timer_start = r[18]*15 # Timer Start	Sum of: 0x01 - 15min, 0x02 - 30min, 0x04 - 1h, 0x08 - 2h, 0x10 - 4h, 0x20 - 8h, 0x40 - 16h 0x80 - invalid
            _current_timerstop = r[19]*15  # Timer Stop	Sum of: 0x01 - 15min, 0x02 - 30min, 0x04 - 1h, 0x08 - 2h, 0x10 - 4h, 0x20 - 8h, 0x40 - 16h 0x80 - invalid
            _current_modeflag = r[21]    # Mode Flags	0x02 - Aux Heat (Turbo), 0x00 - norm, 0x01 - ECO Mode (sleep), 0x04 - SWING, 0x88 VENT
            _current_operflag = r[22]    # Oper Flags	0x04 - water pump running, 0x80 - locked
            _current_error = r[23:24]    # error	E + bit pos, (0..7) + error	E + bit pos, (8..F)
            _current_protect = r[25:26]  # protect P + bit pos, (0..7) + protect	P + bit pos, (8..F)
                 
            #HVAC
            if _current_mode == xye_mode.HEAT:
                self.current_hvac_mode = 'heat'
            else: 
                if _current_mode == xye_mode.COOL:
                    self.current_hvac_mode = 'cool'
                else: 
                    if _current_mode == xye_mode.FAN:
                        self.current_hvac_mode = 'fan_only'
                    else:
                        if _current_mode == xye_mode.OFF:
                            self.current_hvac_mode = 'off'
        
            # SWING
            if _current_modeflag == 4:
                self.current_swing_mode = 'on'
            else:
                self.current_swing_mode = 'off'            
                
            ## RUN STATUS
            if _current_fan_speed != 0:
                self.current_run_status = 'fan'
                if _current_operflag == 4 : 
                    self.current_run_status = 'run' 
            else:
                if _current_protect == b'\x02' :
                    self.current_run_status = 'idle'            
                else:
                    self.current_run_status = 'off'
            
            ## FAN SPEED
            if _current_fan_speed == xye_fan_speed.AUTO:
                self.current_fan_speed = 'auto'
            else:
                if _current_fan_speed == xye_fan_speed.LOW:
                    self.current_fan_speed = 'low'
                else:
                    if _current_fan_speed == xye_fan_speed.MEDIUM:
                        self.current_fan_speed = 'medium'
                    else:
                        if _current_fan_speed == xye_fan_speed.HIGH:
                            self.current_fan_speed = 'high'
                        else:
                            if _current_fan_speed == xye_fan_speed.OFF:
                                self.current_fan_speed = 'off'
            
            if self.request_fan_speed == None:
                self.request_fan_speed = self.current_fan_speed
            
            if self.request_fan_speed == 'auto' :
                _request_fan_speed = xye_fan_speed.AUTO
            else:
                if self.request_fan_speed == 'low' :
                    _request_fan_speed = xye_fan_speed.LOW
                else:
                    if self.request_fan_speed == 'medium' :
                        _request_fan_speed = xye_fan_speed.MEDIUM
                    else:
                        if self.request_fan_speed == 'high' :
                            _request_fan_speed = xye_fan_speed.HIGH
                        else:
                            _request_fan_speed = xye_fan_speed.OFF
            
            self.payload = [_current_mode,_request_fan_speed,self.current_target_temp,_current_timer_start,_current_timerstop,_current_modeflag,0]  

        else:
            xye.desconecta(fancoil)
            xye.conecta(fancoil)
             
            
            
    def _get_data(self):
        _r = xye.query_device(fancoil)
        self._parserespuesta(_r)

    def update(self):
        """Get the latest data."""
        self._get_data()