# Stegnography Android

Android version of the Stegnography app built with Kivy, KivyMD, Pillow, NumPy, Plyer, and Pyjnius.

## Overview

This project hides secret text inside images and later extracts it again using a password-based stop marker. The Android edition keeps the UI in KivyMD, uses Android-aware storage and permissions, and includes an in-app GitHub release checker.

## Features

- Hide text inside RGB or RGBA images
- Extract hidden text using the same password/stop marker
- Choose the source image from a file picker
- Choose the save location for encoded images
- Use a dark-themed KivyMD interface with a navigation drawer
- Support Android 13+ media permissions
- Check GitHub releases and open the download link directly

## Project Layout

```text
Android-Vaersion/
	main.py
	least_significant_bit.py
	update.py
	home.kv
	encode.kv
	decode.kv
	buildozer.spec
	shield.png
	encrypt.png
	decrypt.png
```

## How It Works

1. The user selects a source image.
2. The user enters a secret message and password.
3. The backend writes the message bits into the least significant bits of the image.
4. The app saves the encoded image either to a user-selected path or to the default Pictures/Android storage location.
5. For extraction, the app reads the encoded image, reconstructs the bit stream, and stops at the saved password marker.

## Important Files

- [main.py](main.py): app bootstrap, UI flow, dialogs, storage selection, permission handling, and update prompts
- [least_significant_bit.py](least_significant_bit.py): image encode/decode engine
- [update.py](update.py): GitHub release lookup and direct-download metadata
- [buildozer.spec](buildozer.spec): Android packaging settings
- [home.kv](home.kv): home screen and drawer layout
- [encode.kv](encode.kv): encode screen and save-location controls
- [decode.kv](decode.kv): decode screen and password dialog

## Default Storage Behavior

- Android default output path: `/internal storage/android/encoded images/data`
- Windows and Linux default output path: the user's `Pictures` folder
- A manually selected output path overrides the default for the next encode operation

## Permissions

- `READ_MEDIA_IMAGES` is used on Android 13 and later
- `READ_EXTERNAL_STORAGE` is kept for older Android versions
- `INTERNET` is required for update checks and link opening

## Build

Use Buildozer with the included `buildozer.spec`.

Example:

```bash
buildozer android debug
buildozer android release
```

## Development Notes

- KivyMD widgets and dialogs are written for KivyMD 2.0 compatibility.
- The backend is kept UI-agnostic and raises Python exceptions for invalid inputs.
- The app uses a custom save-file picker so the user can control where encoded images are stored.

## Troubleshooting

- If a widget class is missing at runtime, check for KivyMD 1.x APIs that still need migration.
- If the app cannot open images on Android 13+, verify the media permission prompt was accepted.
- If buildozer pulls a new upstream dependency unexpectedly, pin the package version in `buildozer.spec`.

## License / Attribution

The app uses icon assets from Flaticon. Preserve existing icon attribution notes when redistributing the project.
