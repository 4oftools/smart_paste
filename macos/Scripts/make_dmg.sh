#!/usr/bin/env bash
# 从 Release Archive 生成 DMG（未做公证时，用户首次打开可能需在「隐私与安全性」中允许）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEME="SmartPaste"
ARCHIVE_PATH="${ROOT}/build/SmartPaste.xcarchive"
STAGING="${ROOT}/build/dmg_staging"
DMG_NAME="${DMG_NAME:-SmartPaste}"
DMG_PATH="${ROOT}/build/${DMG_NAME}.dmg"

echo "==> Archive (${SCHEME}, Release, generic macOS)…"
mkdir -p "${ROOT}/build"
xcodebuild archive \
  -project "${ROOT}/SmartPaste.xcodeproj" \
  -scheme "${SCHEME}" \
  -configuration Release \
  -archivePath "${ARCHIVE_PATH}" \
  -destination "generic/platform=macOS" \
  ONLY_ACTIVE_ARCH=NO

APP="${ARCHIVE_PATH}/Products/Applications/${SCHEME}.app"
if [[ ! -d "${APP}" ]]; then
  echo "error: missing ${APP}" >&2
  exit 1
fi

echo "==> Stage for DMG…"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"
ditto "${APP}" "${STAGING}/${SCHEME}.app"
# 常见做法：提供 Applications 替身，方便用户拖拽安装
ln -sf /Applications "${STAGING}/Applications"

echo "==> Create compressed DMG…"
rm -f "${DMG_PATH}"
hdiutil create \
  -volname "${DMG_NAME}" \
  -srcfolder "${STAGING}" \
  -ov \
  -format UDZO \
  "${DMG_PATH}"

echo "==> Done: ${DMG_PATH}"
