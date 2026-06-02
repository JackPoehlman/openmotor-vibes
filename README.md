# OpenMotor Vibes

![Logo](./resources/oMIconCycles.png)

OpenMotor Vibes is a fork of the original [openMotor](https://github.com/reilleya/openMotor), an open-source internal ballistics simulator for rocket motor experimenters.

## Fork Attribution

- Original project: [reilleya/openMotor](https://github.com/reilleya/openMotor)
- Original author: [reilleya](https://github.com/reilleya)
- This fork: [JackPoehlman/openmotor-vibes](https://github.com/JackPoehlman/openmotor-vibes)

This fork keeps compatibility with upstream while adding fork-specific features and tooling. See [CHANGELOG.md](CHANGELOG.md) for fork changes and upstream sync notes.

## Overview

OpenMotor estimates chamber pressure and thrust from propellant properties, grain geometry, and nozzle specifications. It uses the Fast Marching Method to model grain regression, including arbitrary core geometries.

- Metric and imperial units
- Support for common grain geometries (BATES, Finocyl, Star, and more)
- Loading custom grain geometry from DXF files
- Propellant editor for custom propellant libraries
- Grain regression visualization in the grain editor
- ENG file export
- BurnSim import and export
- Save/load with undo and redo support
- Design optimization and analysis tools

## What This Fork Adds

OpenMotor Vibes includes fork-specific improvements on top of upstream openMotor:

### New Tools and Data

- Hardware catalog browser (hardware picker) for selecting supported motor cases and nozzles
- Grain preset picker to quickly initialize common grain configurations
- Bundled hardware catalog and hardware weights datasets used by the picker workflows
- NozzleCoeffTool for back-calculating throat erosion and slag coefficients

### UI and Workflow Improvements

- Casing visualization added to the nozzle preview widget
- Propellant diameter shown in motor statistics (alongside propellant length)
- Tool input memory so tool dialogs remember prior inputs between runs

### Simulation and Robustness Changes

- Relaxed grain size limits to support a wider range of motor geometries
- Improved core Mach behavior near burn start/end to avoid spurious high values
- Improved handling of invalid preference and propellant files
- Support for longer design designations
- Improved error wording in thrust-related calculations to mention Kn

See [CHANGELOG.md](CHANGELOG.md) for full details and ongoing updates.

The calculations are based on Rocket Propulsion Elements by George Sutton and [Richard Nakka's work](https://www.nakka-rocketry.net/rtheory.html).

![Screenshot](https://reilley.net/openMotor/screenshot.png)

## Downloads and Installers

### OpenMotor Vibes (this fork)

Get the latest fork release, including packaged binaries and installer artifacts, from:

- [OpenMotor Vibes latest release](https://github.com/JackPoehlman/openmotor-vibes/releases/latest)
- [Windows installer script (Inno Setup)](./installers/windows.iss)

Maintainers: see [GITHUB_SETUP.md](./GITHUB_SETUP.md) for the release publishing checklist (including installer asset upload).

### Original openMotor (upstream)

Get the original project's release builds from:

- [openMotor latest release](https://github.com/reilleya/openMotor/releases/latest)

Use the fork release if you want fork-specific features. Use upstream if you want the original project exactly as maintained by upstream.

## Building from Source

The project is currently developed with Python 3.10. Dependencies are listed in requirements.txt (notably PyQt6, matplotlib, numpy, scipy, scikit-fmm, and scikit-image).

### Quick setup

1. Clone this fork repository.
2. Create and activate a virtual environment.
3. Install dependencies from requirements.txt.

If dependency builds fail with missing Python headers (for example while building scikit-fmm), install your system's Python development package (for example python3-dev on Debian/Ubuntu).

On Windows, if you encounter DLL load errors after dependency installation, install the latest Microsoft Visual C++ Redistributable.

### UI files

OpenMotor uses Qt Designer .ui files that must be compiled before running from source:

- python setup.py build_ui

If you edit .ui forms, rerun the same command.

### Cython files

Some performance-critical code is compiled with Cython and must be built per platform:

- python setup.py build_ext --inplace

If you edit .pyx files, rerun this command.

### Run the application

- python main.py

## Data Files

Motor files use YAML with the .ric extension. The recommended MIME type is application/vnd.openmotor+yaml.

User files such as preferences and propellant libraries are stored in platform app-data locations:

- Windows: <AppData>\Local\openMotor
- macOS: /Users/<username>/Library/Application Support/openMotor
- Linux: /home/<username>/.local/share/openMotor

## Contributing

Contributions are welcome. If you find a bug or have an idea, open an issue or submit a pull request.

If reporting a bug, please indicate whether it reproduces in upstream openMotor or only in this fork.

## License

OpenMotor Vibes is released under GNU GPL v3, consistent with the upstream project.

## Disclaimer

Rocket motors can be dangerous. Always verify calculations before testing and conduct testing at safe distances from people and structures. This software provides estimates only, with no guarantees.
