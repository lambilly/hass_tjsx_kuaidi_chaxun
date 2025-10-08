# 天聚数行-快递查询 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

这是一个 Home Assistant 自定义集成，用于查询快递物流信息，基于天聚数行 API 开发。

## 功能特点

- 🔍 实时查询快递物流信息
- 📦 支持多家快递公司
- ⏰ 自动停止更新已签收快递
- 📱 完整的物流轨迹展示
- 🎯 清理客服提示信息
- 🔄 可配置查询周期

## 安装

### 方法一：通过 HACS（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 的 "Integrations" 页面，点击右上角的三个点菜单，选择 "Custom repositories"
3. 在弹出窗口中添加仓库地址：`https://github.com/lambilly/hass_tjsx_kuaidi_chaxun/`，类别选择 "Integration"
4. 在 HACS 中搜索 "天聚数行-快递查询"
5. 点击下载
6. 重启 Home Assistant

### 方法二：手动安装

1. 下载此仓库的 ZIP 文件
2. 解压后将 `custom_components/tjsx_kuaidi_chaxun` 文件夹复制到您的 Home Assistant 的 `custom_components` 目录
3. 重启 Home Assistant

## 配置

### 获取 API Key

1. 访问 [天聚数行官网](https://www.tianapi.com/)
2. 注册账号并登录
3. 在控制台获取 API Key
4. 注意：该 API 按次计费，每次请求 0.01 元

### 在 Home Assistant 中配置

1. 进入 Home Assistant → 设置 → 设备与服务 → 集成
2. 点击"添加集成"，搜索"天聚数行-快递查询"
3. 首次添加时需要输入 API Key
4. 后续添加只需输入快递单号和自定义名称（可选）
5. 设置查询周期（默认 12 小时）

## 实体属性

每个快递查询实体包含以下属性：

- **状态**: 快递当前状态（无记录、揽件、在途中、派送中、已签收等）
- **快递单号**: 完整的快递单号
- **快递公司**: 快递公司名称
- **最新动态**: 清理后的最新物流信息
- **物流轨迹**: 完整的物流轨迹列表
- **联系电话**: 快递公司联系电话
- **查询时间**: 最后一次查询的时间
- **已签收**: 是否已签收（用于停止自动更新）

## 快递状态说明

| 状态码 | 状态说明 |
|--------|----------|
| 0 | 无记录 |
| 1 | 揽件 |
| 2 | 在途中 |
| 3 | 派送中 |
| 4 | 已签收 |
| 5 | 用户拒签 |
| 6 | 疑难件 |
| 7 | 无效单 |
| 8 | 超时单 |
| 9 | 签收失败 |
| 10 | 退回 |
| 11 | 转投 |
| 12 | 待签 |

## 自动化示例

```yaml
# 当快递签收时发送通知
alias: "快递签收通知"
trigger:
  - platform: state
    entity_id: sensor.your_express_number
    to: "已签收"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "快递已签收"
      message: "您的快递 {{ state_attr('sensor.your_express_number', '快递单号') }} 已签收"
```
# 注意事项
•	快递签收后，集成会自动停止定期查询以节省 API 调用
•	如需重新启用查询，请删除并重新添加该快递单号
•	请合理设置查询周期，避免不必要的 API 调用费用
# 支持
如遇到问题，请：
1.	检查 Home Assistant 日志
2.	确认 API Key 有效且有余额
3.	确认快递单号正确
4.	在 GitHub Issues 提交问题
# 许可证
MIT License
# 贡献
欢迎提交 Pull Request 和 Issue！


