# Spawn Workflow

This is the intended repeatable flow for creating a new Fox Mountain app from the template.

## Command

From the template repo:

```sh
python3 scripts/spawn_app.py "Unit Converter"
```

Optional:

```sh
python3 scripts/spawn_app.py "Unit Converter" --bundle-id dev.foxmountain.unitconverter --destination-root /custom/path
```

## Default Destination

If no destination root is provided, the script creates the new app under:

```text
../fms/apps/spawned/<app-slug>
```

Example:

```text
/Users/openclaw/.openclaw/workspace/fms/apps/spawned/unit-converter
```

## What the Script Does

- copies the template into a new app folder
- excludes `.git`, generated Xcode project files, and derived build artifacts
- rewrites key placeholder text:
  - app name
  - bundle ID
  - human-readable placeholders
  - local FoxMountainKit path relative to the spawned app location
- renames `Sources/QuickNoteFinalRehearsal` to a generated app-specific source folder
- renames the placeholder test file
- changes the generated project and scheme name via rewritten `project.yml`

## What It Does Not Yet Do

- generate app-specific icons
- create App Store Connect records
- wire production secrets
- rewrite every placeholder we may add in future files automatically

## Immediate Follow-Up After Spawn

```sh
cd /path/to/new/app
xcodegen generate
xcodebuild -project <GeneratedName>.xcodeproj -scheme <GeneratedName> -destination 'generic/platform=iOS Simulator' build
```

Example:

```sh
cd /Users/openclaw/.openclaw/workspace/fms/apps/spawned/unit-converter
xcodegen generate
xcodebuild -project UnitConverter.xcodeproj -scheme UnitConverter -destination 'generic/platform=iOS Simulator' build
```

Then:
- replace placeholder UI
- update App Store metadata
- review monetization/analytics config
- update icons/assets
- prepare TestFlight/App Store deployment
