# aw_watcher_screenshot

`aw_watcher_screenshot` is a utility for taking screenshots of active windows
and saving them in a specific format. It integrates with ActivityWatch and
provides configurable options for automatic screenshot capture based on window
activity.

## Installation

To install `aw_watcher_screenshot`, use [Poetry](https://python-poetry.org/), a
Python dependency management and packaging tool. Simply run the following
command:

```bash
poetry install
```

## Usage

After installation, you can run the `aw-watcher-screenshot` tool using Poetry:

```bash
poetry run aw-watcher-screenshot
```

This will start the tool according to the configuration settings.


## Command-Line Arguments

The `aw_watcher_screenshot` tool supports the following command-line arguments:

### `--host`
- **Description**: Specifies the host to connect to.
- **Type**: `str`
- **Default**: 127.0.0.1

### `--port`
- **Description**: Specifies the port to connect to.
- **Type**: `int`
- **Default**: 5600

### `--testing`
- **Description**: Enables testing mode, which can be used for debugging or testing purposes. Port is set to 5666.

### `--exclude-title`
- **Description**: If set, excludes the window title from being captured in screenshots.

### `--on_window_change`
- **Description**: If set, screenshots will only be taken when the active window changes.
- **Type**: `flag (store_true)`
- **Default**: `False` (based on configuration)

### `--exclude-titles`
- **Description**: A list of window titles (regular expressions) to exclude from being captured. Can be specified multiple times.
- **Type**: `list of str`
- **Default**: Empty list (based on configuration)

### `--verbose`
- **Description**: Enables verbose output for debugging and more detailed logs.

### `--poll-time`
- **Description**: The interval (in seconds) for polling the active window. This determines how often the tool checks the active window.
- **Type**: `float`
- **Default**: `20.0` (based on configuration)

### `--strategy`
- **Description**: The strategy to use for retrieving the active window on macOS. Supported options are:
  - `jxa`: Use JavaScript for Automation.
  - `applescript`: Use AppleScript.
  - `swift`: Use Swift (default).
- **Type**: `str`
- **Default**: `swift` (based on configuration)
- **macOS-only**: This option is only available for macOS.

### `--name_template`
- **Description**: Template for naming the screenshot files. The template can include placeholders such as `{mon}` for the monitor and `{date}` for the timestamp.
- **Type**: `str`
- **Default**: `"monitor_{mon}_{date}.png"` (based on configuration)

## Configuration

The default configuration for `aw_watcher_screenshot` is as follows:

```toml
[aw-watcher-screenshot]
exclude_title = false
exclude_titles = []
poll_time = 20.0
on_window_change = false
name_template = "monitor_{mon}_{date}.png"
strategy_macos = "swift"
```

## Configuration Location

Configurations are saved in the ActivityWatch config folder. On Linux, the storage location is:

```
~/.config/activitywatch/aw-watcher-screenshot/aw-watcher-screenshot.toml
```

### Configuration Options:

- `exclude_title` (default: `false`): Whether to exclude the window title from being captured in screenshots.
- `exclude_titles` (default: `[]`): A list of window titles to exclude from the screenshot capture.
- `poll_time` (default: `20.0`): The polling interval (in seconds) for checking active windows.
- `on_window_change` (default: `false`): Whether to take screenshots only when the window changes.
- `name_template` (default: `"monitor_{mon}_{date}.png"`): A template for naming the screenshots. `{mon}` is replaced with the monitor name, and `{date}` with the timestamp of the capture.
- `strategy_macos` (default: `"swift"`): The strategy used for capturing windows on macOS (using Swift).

## Storage Location

Screenshots are saved in the ActivityWatch data folder. On Linux, the storage location is:

```
~/.local/share/activitywatch/aw-watcher-screenshot/
```
