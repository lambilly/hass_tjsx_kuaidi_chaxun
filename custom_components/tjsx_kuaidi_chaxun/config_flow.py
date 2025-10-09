"""Config flow for TJSX Kuaidi Chaxun integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_EXPRESS_NUMBER,
    CONF_EXPRESS_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class TJSXKuaidiChaxunConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TJSX Kuaidi Chaxun."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._api_key = None
        self._express_data = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # 检查是否已经配置过API密钥
        existing_entries = self._async_current_entries()
        if existing_entries:
            # 如果已经配置过，直接跳转到添加快递单号
            return await self.async_step_express()

        if user_input is not None:
            # 首次配置：收集API密钥
            self._api_key = user_input[CONF_API_KEY]
            return await self.async_step_express()

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={}
        )

    async def async_step_express(self, user_input=None):
        """Handle the express configuration step."""
        errors = {}

        if user_input is not None:
            # 使用快递单号作为默认名称
            express_name = user_input.get(CONF_EXPRESS_NAME, user_input[CONF_EXPRESS_NUMBER])
            
            # 获取API密钥（从现有配置或当前输入）
            api_key = self._api_key
            if not api_key:
                existing_entries = self._async_current_entries()
                if existing_entries:
                    api_key = existing_entries[0].data.get(CONF_API_KEY)
            
            # 检查是否已存在相同的快递单号
            for entry in self._async_current_entries():
                if entry.data.get(CONF_EXPRESS_NUMBER) == user_input[CONF_EXPRESS_NUMBER]:
                    return self.async_abort(reason="already_configured")
            
            # 创建配置条目
            data = {
                CONF_API_KEY: api_key,
                CONF_EXPRESS_NUMBER: user_input[CONF_EXPRESS_NUMBER],
                CONF_EXPRESS_NAME: express_name,
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            }

            return self.async_create_entry(
                title=express_name,
                data=data
            )

        data_schema = vol.Schema({
            vol.Required(CONF_EXPRESS_NUMBER): str,
            vol.Optional(CONF_EXPRESS_NAME): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=24)
            ),
        })

        return self.async_show_form(
            step_id="express",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TJSXKuaidiChaxunOptionsFlow(config_entry)

class TJSXKuaidiChaxunOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for TJSX Kuaidi Chaxun."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # 更新配置条目数据
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]
                }
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
            })
        )