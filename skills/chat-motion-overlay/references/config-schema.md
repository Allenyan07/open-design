# Config Schema

Provide a JSON file when the user wants anything beyond the defaults.

## Example

```json
{
  "container": "wechat",
  "avatarMode": "mixed",
  "deviceFrame": "iphone-dynamic-island",
  "nicknameMode": "first-message-only",
  "deliveryFormat": "mov",
  "showTimestamp": true,
  "avatarAssignments": {
    "leftPreset": "female-bunny-pink",
    "rightPreset": "female-cat-orange",
    "leftUploadPath": null,
    "rightUploadPath": null
  }
}
```

## Fields

- `container`
  - `none`: standalone bubbles only
  - `wechat`: WeChat-style UI shell
  - `telegram`: Telegram-like UI shell
  - `messenger`: Facebook Messenger-like UI shell

- `avatarMode`
  - `preset`: use only bundled preset avatars
  - `upload`: use only uploaded avatar files
  - `mixed`: combine preset on one side and upload on the other

- `deviceFrame`
  - `none`
  - `iphone-dynamic-island`

- `nicknameMode`
  - `hidden`
  - `first-message-only`
  - `always`

- `deliveryFormat`
  - `mov`: `MOV（透明背景，可直接导入剪映 / PR / FCP 叠加）`
  - `webm`: `WebM（透明背景，适合网页 / 浏览器播放）`
  - `remotion`: `Remotion 工程（适合继续编辑和拼装）`
  - `hyperframe`: `Hyperframe 工程（适合作为模块继续复用）`
  - `json`: `JSON 数据（适合程序处理 / 自定义渲染）`
  - `preview`: `预览图 / 预览工程（适合先确认效果）`

- `showTimestamp`
  - boolean

- `avatarAssignments`
  - `leftPreset`, `rightPreset`
  - `leftUploadPath`, `rightUploadPath`

## Preset Avatar Keys

- `female-bunny-pink`
- `female-cat-orange`
- `female-fox-yellow`
- `male-bear-mint`
- `male-penguin-blue`
- `male-koala-lilac`
