# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## About openmotor-vibes

This is a fork of the original [openMotor](https://github.com/reilleya/openMotor) by [reilleya](https://github.com/reilleya). This fork is maintained to add custom enhancements and improvements while staying compatible with upstream releases.

### Upstream Synchronization

This fork is periodically rebased on upstream openMotor releases. To see the full history of changes from the original project, visit the [upstream repository](https://github.com/reilleya/openMotor).

---

## [Unreleased]

### Added
- **NozzleCoeffTool** - Back-calculate throat erosion and slag coefficients for nozzle analysis
- **Casing section** in nozzle preview widget for enhanced nozzle visualization
- **Propellant diameter display** in motor statistics alongside propellant length
- **Tool input memory** - Tool inputs are now remembered between runs for improved workflow

### Changed
- Relaxed grain size limits to support more diverse motor designs
- Improved error messaging to mention Kn (characteristic velocity) in thrust calculations
- Updated grain and geometry type hints and associated tests for better code quality
- Formatting and import structure improvements across motorlib

### Fixed
- Fixed spurious high core Mach numbers caused by chamber pressure dropping at beginning or end of burn
- Fixed core Mach calculation issues
- Fixed issue with grain perimeter calculation using rewritten method
- Fixed design designation handling to support arbitrarily long designations
- Fixed handling of invalid preference and propellant files to degrade gracefully
- Fixed design designation support for longer motor designations

### Removed
- Unused imports cleanup across motorlib modules

---

## Fork Contributions

### Key Modifications from Original

| File/Component | Change | Reason |
|---|---|---|
| motorlib/motor.py | Enhanced core Mach calculation | Fixed spurious high Mach numbers at burn start/end |
| uilib/tools/nozzleCoeff.py | New NozzleCoeffTool | Enable back-calculation of throat erosion coefficients |
| uilib/widgets/nozzlePreviewWidget.py | Added casing visualization | Improved nozzle design preview |
| motorlib/grain.py | Relaxed size limits | Support wider range of motor geometries |
| uilib/simulationManager.py | Tool input persistence | Better workflow - remember previous inputs |

### Contributors
- JackPoehlman - Fork creator and maintainer

---

## Upstream Version Tracking

This fork is based on upstream openMotor commit: `da7f410` ("Gracefully handle invalid preference/propellant files")

Last sync with upstream: April 25, 2026

### Notable Upstream Releases
- openMotor v0.6.1 - Latest stable baseline for this fork (tag: v0.6.1, upstream/fix_actions)

---

## How to Report Issues

- For issues specific to openmotor-vibes: Use this repository's issue tracker
- For issues in the original openMotor: Visit https://github.com/reilleya/openMotor/issues
- When reporting, clearly indicate whether the issue exists in upstream or is specific to vibes fork
