# Test Matrix

This matrix covers the configurable surface of `$chat-motion-overlay`.

## Goals

- Validate transcript to spec generation
- Validate bundle preparation and asset copying
- Validate template type safety
- Validate representative rendering for each major scene family
- Catch invalid config combinations early
- Validate group chats can assign avatars per participant instead of only per side
- Lock down the question strategy so incomplete requests are handled consistently

## Covered Dimensions

- `container`: `none`, `wechat`, `telegram`, `messenger`
- `avatarMode`: `preset`, `upload`, `mixed`
- `deviceFrame`: `none`, `iphone-dynamic-island`
- `nicknameMode`: `hidden`, `first-message-only`, `always`
- `deliveryFormat`: `mov`, `webm`, `json`, `remotion`, `hyperframe`, `preview`

## Cases

1. `default_wechat_phone_preset_hidden`
   - Container: `wechat`
   - Avatar mode: `preset`
   - Device frame: `iphone-dynamic-island`
   - Nickname mode: `hidden`
   - Delivery: `MOV（透明背景，可直接导入剪映 / PR / FCP 叠加）`

2. `plain_bubbles_no_frame_first_message`
   - Container: `none`
   - Avatar mode: `preset`
   - Device frame: `none`
   - Nickname mode: `first-message-only`
   - Delivery: `Remotion 工程（适合继续编辑和拼装）`

3. `telegram_no_frame_always`
   - Container: `telegram`
   - Avatar mode: `preset`
   - Device frame: `none`
   - Nickname mode: `always`
   - Delivery: `WebM（透明背景，适合网页 / 浏览器播放）`

4. `messenger_phone_hidden`
   - Container: `messenger`
   - Avatar mode: `preset`
   - Device frame: `iphone-dynamic-island`
   - Nickname mode: `hidden`
   - Delivery: `MOV（透明背景，可直接导入剪映 / PR / FCP 叠加）`

5. `upload_phone_always`
   - Container: `wechat`
   - Avatar mode: `upload`
   - Device frame: `iphone-dynamic-island`
   - Nickname mode: `always`
   - Delivery: `MOV（透明背景，可直接导入剪映 / PR / FCP 叠加）`

6. `mixed_wechat_phone_first_message`
   - Container: `wechat`
   - Avatar mode: `mixed`
   - Device frame: `iphone-dynamic-island`
   - Nickname mode: `first-message-only`
   - Delivery: `Hyperframe 工程（适合作为模块继续复用）`

7. `json_spec_only`
   - Container: `wechat`
   - Avatar mode: `preset`
   - Device frame: `iphone-dynamic-island`
   - Nickname mode: `hidden`
   - Delivery: `JSON 数据（适合程序处理 / 自定义渲染）`

8. `group_multi_participant_distinct_presets`
   - Container: `wechat`
   - Avatar mode: `preset`
   - Four speakers across left and right sides
   - Expected: each participant can resolve to a distinct avatar

9. `invalid_upload_missing_side`
   - Avatar mode: `upload`
   - Missing one upload path
   - Expected: fail with validation error

10. `invalid_mixed_without_upload`
   - Avatar mode: `mixed`
   - No upload path
   - Expected: fail with validation error

11. `invalid_upload_missing_file`
   - Avatar mode: `upload`
   - Upload path points to a missing file
   - Expected: bundle preparation fails fast with a clear missing-file error

12. `invalid_participant_side_conflict`
   - One participant appears on both left and right sides
   - Expected: fail with validation error and ask for consistent participant side

## Pass Criteria

- Valid cases generate JSON spec successfully
- Valid bundle cases prepare output bundle successfully
- Generated bundle sanitizes machine-local upload paths out of `src/chatSpec.ts`
- Generated bundle passes `tsc --noEmit`
- Representative valid cases render a still frame successfully
- Group chat cases assign avatars by participant, not only by left/right side
- Participant side conflicts fail instead of rendering one person on both sides
- Invalid cases fail with the expected validation error
- Invalid upload-path cases fail during bundle preparation instead of silently falling back to preset avatars
- Question policy is documented with defaults, triggers, and user-facing wording
