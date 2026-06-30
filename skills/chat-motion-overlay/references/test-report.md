# Test Report

Date: 2026-06-28

## Scope

Validated the new `$chat-motion-overlay` skill across:

- transcript -> spec generation
- config validation
- bundle preparation
- preset avatar asset copying
- uploaded avatar asset copying
- generated bundle sanitization for uploaded avatar paths
- group chat participant-level avatar assignment
- participant side consistency validation
- Remotion template type safety
- representative still rendering
- documented question strategy for incomplete requests

## Matrix Result

- Total cases: 12
- Passed: 12
- Failed: 0

## Covered Cases

1. `default_wechat_phone_preset_hidden`
2. `plain_bubbles_no_frame_first_message`
3. `telegram_no_frame_always`
4. `messenger_phone_hidden`
5. `upload_phone_always`
6. `mixed_wechat_phone_first_message`
7. `json_spec_only`
8. `group_multi_participant_distinct_presets`
9. `invalid_upload_missing_side`
10. `invalid_mixed_without_upload`
11. `invalid_upload_missing_file`
12. `invalid_participant_side_conflict`

## Issues Found And Fixed

1. `chatSpec.ts` generated readonly arrays while template types expected mutable arrays.
   - Fix: changed template `ChatSpec` types to use `ReadonlyArray`.

2. Config validation for `avatarMode=upload` and `avatarMode=mixed` was too loose.
   - Fix: added explicit validation in `build_chat_overlay_spec.py`.
   - Update: `avatarMode=upload` now requires uploaded avatar paths on participant configs.

3. New skill needed bundled preset avatar assets available in generated Remotion bundles.
   - Fix: added avatar library copying in `prepare_chat_overlay_bundle.py`.

4. User-facing output choices were too technical.
   - Fix: replaced direct `output` selection with `deliveryFormat`, then mapped it internally to render targets and artifact modes.

5. Incomplete user requests needed a consistent clarification strategy.
   - Fix: added a documented question policy with defaults, question limits, and user-facing wording.

6. Missing uploaded avatar files could silently fall back to preset avatars during bundle preparation.
   - Fix: made `prepare_chat_overlay_bundle.py` fail fast when a configured upload path does not exist, and added bundle-stage coverage for that case.

7. Group chats needed participant-level avatars instead of only side-level avatars.
   - Fix: replaced side-level avatar assignment with participant-level preset and upload assignment support.

8. One speaker could be interpreted on both sides if the transcript conflicted.
   - Fix: added participant side consistency validation.

## Verification Notes

- Representative bundles were rendered to still images successfully.
- Invalid config cases failed with the expected validation errors.
- Invalid uploaded-avatar file paths failed during bundle preparation with a clear error.
- Generated `chatSpec.ts` bundles kept only participant `uploadAsset` entries and did not leak local `uploadPath` values.
- Group chat participants resolved to distinct participant avatars instead of sharing side-level avatars.
- Side conflicts for a single participant failed with a clear validation error.
- Bundle type checking passed with `tsc --noEmit`.

## References

- Test matrix: `references/test-matrix.md`
- Test runner: `scripts/run_test_matrix.py`
