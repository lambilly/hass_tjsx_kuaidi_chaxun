"""The TJSX Kuaidi Chaxun integration."""
import logging
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_EXPRESS_NUMBER,
    CONF_EXPRESS_NAME,
    DEFAULT_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TJSX Kuaidi Chaxun component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TJSX Kuaidi Chaxun from a config entry."""
    # 创建设备（只在第一个配置条目时创建）
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "express_query_device")},
        name="快递查询",
        manufacturer="天聚数行",
        model="快递查询",
        sw_version="1.0.0"
    )
    
    # 存储设备ID供传感器使用
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["device_id"] = device_entry.id
    
    # 存储配置条目数据
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # 设置传感器平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # 如果没有更多配置条目，清理设备数据
        if len(hass.data[DOMAIN]) <= 2:  # device_id + 可能的其他数据
            hass.data[DOMAIN].pop("device_id", None)
    
    return unload_ok