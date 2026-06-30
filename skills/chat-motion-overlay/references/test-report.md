# Test Report

Date: 2026-06-28

## Scope

Validated the new `$chat-motion-overlay` skill across:

- transcript -> spec generation
- config validation
- bundle preparation
- preset avatar asset copying
- uploaded avatar asset copying
- Remotion template type safety
- representative still rendering
- documented question strategy for incomplete requests

## Matrix Result

- Total cases: 9
- Passed: 9
- Failed: 0

## Covered Cases

1. `default_wechat_phone_preset_hidden`
2. `plain_bubbles_no_frame_first_message`
3. `telegram_no_frame_always`
4. `messenger_phone_hidden`
5. `upload_phone_always`
6. `mixed_wechat_phone_first_message`
7. `json_spec_only`
8. `invalid_upload_missing_side`
9. `invalid_mixed_without_upload`

## Issues Found And Fixed

1. `chatSpec.ts` generated readonly arrays while template types expected mutable arrays.
   - Fix: changed template `ChatSpec` types to use `ReadonlyArray`.

2. Config validation for `avatarMode=upload` and `avatarMode=mixed` was too loose.
   - Fix: added explicit validation in `build_chat_overlay_spec.py`.

3. New skill needed bundled preset avatar assets available in generated Remotion bundles.
   - Fix: added avatar library copying in `prepare_chat_overlay_bundle.py`.

4. User-facing output choices were too technical.
   - Fix: replaced direct `output` selection with `deliveryFormat`, then mapped it internally to render targets and artifact modes.

5. Incomplete user requests needed a consistent clarification strategy.
   - Fix: added a documented question policy with defaults, question limits, and user-facing wording.

## Verification Notes

- Representative bundles were rendered to still images successfully.
- Invalid config cases failed with the expected validation errors.
- Bundle type checking passed with `tsc --noEmit`.

## References

- Test matrix: `references/test-matrix.md`
- Test runner: `scripts/run_test_matrix.py`
