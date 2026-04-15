fastlane documentation
----

# Installation

Make sure you have the latest version of the Xcode command line tools installed:

```sh
xcode-select --install
```

For _fastlane_ installation instructions, see [Installing _fastlane_](https://docs.fastlane.tools/#installing-fastlane)

# Available Actions

## iOS

### ios adhoc

```sh
[bundle exec] fastlane ios adhoc
```

Deploy to Ad Hoc - Usage: fastlane adhoc project:'path/to/App.xcodeproj' scheme:'AppScheme'

### ios testflight

```sh
[bundle exec] fastlane ios testflight
```

Deploy to TestFlight - Usage: fastlane testflight project:'path/to/App.xcodeproj' scheme:'AppScheme'

----

This README.md is auto-generated and will be re-generated every time [_fastlane_](https://fastlane.tools) is run.

More information about _fastlane_ can be found on [fastlane.tools](https://fastlane.tools).

The documentation of _fastlane_ can be found on [docs.fastlane.tools](https://docs.fastlane.tools).
