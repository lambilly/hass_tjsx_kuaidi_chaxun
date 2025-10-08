"""Sensor platform for TJSX Kuaidi Chaxun integration."""
import logging
import asyncio
from datetime import timedelta
import aiohttp
import async_timeout
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_EXPRESS_NUMBER,
    CONF_EXPRESS_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    STATUS_MAP,
    API_URL
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    api_key = config_entry.data[CONF_API_KEY]
    express_number = config_entry.data[CONF_EXPRESS_NUMBER]
    express_name = config_entry.data.get(CONF_EXPRESS_NAME, express_number)
    scan_interval = config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = TJSXKuaidiChaxunDataUpdateCoordinator(
        hass,
        api_key,
        express_number,
        express_name,
        scan_interval
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([TJSXKuaidiChaxunSensor(coordinator, config_entry)])

class TJSXKuaidiChaxunDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TJSX Kuaidi data."""

    def __init__(self, hass, api_key, express_number, express_name, scan_interval):
        """Initialize."""
        self.api_key = api_key
        self.express_number = express_number
        self.express_name = express_name
        self._last_update_time = None
        self._is_delivered = False  # 标记快递是否已签收

        update_interval = timedelta(hours=scan_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=express_name,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Update data via API."""
        # 如果快递已签收，不再更新数据
        if self._is_delivered:
            _LOGGER.info(f"快递 {self.express_number} 已签收，停止定期更新")
            return None
            
        try:
            async with async_timeout.timeout(10):
                data = await self._fetch_express_data()
                self._last_update_time = dt_util.utcnow()
                
                # 检查快递状态，如果是"已签收"状态，标记为已送达
                if data and data.get("code") == 200:
                    result = data.get("result", {})
                    status = result.get("status")
                    if status == 4:  # 4表示已签收
                        self._is_delivered = True
                        _LOGGER.info(f"快递 {self.express_number} 已签收，将停止定期更新")
                
                return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_express_data(self):
        """Fetch express data from the API."""
        url = f"{API_URL}?key={self.api_key}&number={self.express_number}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"HTTP error: {response.status}")
                
                data = await response.json()
                
                if data.get("code") != 200:
                    error_msg = data.get("msg", "Unknown error")
                    raise UpdateFailed(f"API error: {error_msg}")
                
                return data

    @property
    def last_update_time(self):
        """Return the last successful update time."""
        return self._last_update_time
        
    @property
    def is_delivered(self):
        """Return whether the package has been delivered."""
        return self._is_delivered

class TJSXKuaidiChaxunSensor(CoordinatorEntity, SensorEntity):
    """Representation of a TJSX Kuaidi Chaxun Sensor."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        express_name = config_entry.data.get(CONF_EXPRESS_NAME)
        express_number = config_entry.data[CONF_EXPRESS_NUMBER]
        
        # 如果没有设置快递名称，使用快递单号
        self._attr_name = express_name if express_name else express_number
        self._attr_unique_id = f"{config_entry.entry_id}_{express_number}"
        
        # 设置设备信息
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "express_query_device")},
            name="快递查询",
            manufacturer="天聚数行",
            model="快递查询",
            sw_version="1.0.0"
        )

    def _clean_content(self, content):
        """清理content中的客服提示信息"""
        if not content:
            return content
            
        # 移除类似【如有问题请拨打速递官方客服956160，高效响应，快速解决】的提示
        pattern = r'【[^】]*客服\d+[^】]*】'
        cleaned_content = re.sub(pattern, '', content)
        
        # 清理多余的空格
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
        
        return cleaned_content

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return "未知"
            
        result = self.coordinator.data.get("result", {})
        status = result.get("status")
        return STATUS_MAP.get(status, "未知")

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
            
        result = self.coordinator.data.get("result", {})
        
        # 安全地获取查询时间
        query_time = ""
        if hasattr(self.coordinator, 'last_update_time') and self.coordinator.last_update_time:
            query_time = self.coordinator.last_update_time.isoformat()
        
        # 处理最新动态
        latest_dynamic = ""
        if result.get("list"):
            latest_track = result["list"][0]
            raw_content = latest_track.get("content", "")
            latest_dynamic = self._clean_content(raw_content)
        
        attributes = {
            "快递单号": self.config_entry.data[CONF_EXPRESS_NUMBER],
            "快递公司": result.get("kuaidiname", ""),
            "英文快递公司": result.get("enkuaidiname", ""),
            "状态码": result.get("status"),
            "最后更新时间": result.get("updatetime", ""),
            "联系电话": result.get("telephone", ""),
            "物流轨迹": result.get("list", []),
            "查询时间": query_time,
            "轨迹数量": len(result.get("list", [])),
            "最新动态": latest_dynamic,
            "已签收": self.coordinator.is_delivered,
        }
        
        # 保留原有的最新轨迹信息（已清理过的）
        if result.get("list"):
            latest_track = result["list"][0]
            attributes["最新轨迹时间"] = latest_track.get("time", "")
            attributes["最新轨迹内容"] = self._clean_content(latest_track.get("content", ""))
            attributes["最新轨迹地点"] = latest_track.get("address", "")
        
        return attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self.coordinator.data is None:
            return "mdi:package-variant"
            
        status = self.coordinator.data.get("result", {}).get("status")
        if status == 4:  # 已签收
            return "mdi:package-variant-closed-check"
        elif status in [2, 3]:  # 在途中, 派送中
            return "mdi:truck-delivery"
        elif status in [5, 6, 7, 9, 10]:  # 问题状态
            return "mdi:alert-circle"
        else:
            return "mdi:package-variant"
            
    @property
    def available(self):
        """Return if entity is available."""
        # 即使快递已签收，实体仍然可用，只是不再更新数据
        return True