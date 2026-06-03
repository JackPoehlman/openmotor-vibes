# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## About OpenMotor Vibes

This is a fork of the original [openMotor](https://github.com/reilleya/openMotor) by [reilleya](https://github.com/reilleya). This fork is maintained to add custom enhancements and improvements while staying compatible with upstream releases.

### Upstream Synchronization

This fork is periodically rebased on upstream openMotor releases. To see the full history of changes from the original project, visit the [upstream repository](https://github.com/reilleya/openMotor).

---

## [Unreleased]

### Added
- No changes yet.

### Changed
- No changes yet.

### Fixed
- No changes yet.

### Removed
- No changes yet.

---

## [0.6.3] - 2026-06-02

### Fixed
- Fixed a contour edge-case in the Python perimeter fallback (`mathlib/_find_perimeter_py.py`) for marching-squares case 14. This resolves incorrect segment stitching that could break regression visualizer output and area graph rendering in some grain states.
- Fixed stale preview updates in the grain preview pipeline by guarding background results with request IDs, preventing older worker results from overwriting newer UI state.

### Changed
- Refactored grain preview generation (`uilib/widgets/grainPreviewWidget.py`) to split fast face preview rendering from heavier regression and area generation.
- Regression and area previews are now generated lazily (only when those tabs are active), which significantly improves responsiveness while editing grain parameters.
- Added staged preview quality updates with an idle full-refresh pass to keep interaction smooth during rapid changes while still converging to full-quality output.
- Added core perimeter memoization in `motorlib/grain.py` so repeated perimeter queries reuse computed values instead of recomputing every call.

### Performance
- Improved setup and interaction speed for heavy grains (especially Finocyl and Moonburner) by reducing repeated perimeter and FMM-driven work during live UI updates.
- Reduced UI lag when tweaking complex grain geometry by avoiding unnecessary regression visualization work until needed.

### Packaging and Release
- Published a fresh Windows installer for this release: OpenMotorVibes-Setup.exe.

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

This fork is based on upstream openMotor commit: da7f410 ("Gracefully handle invalid preference/propellant files")

Last sync with upstream: April 25, 2026

### Notable Upstream Releases
- openMotor v0.6.1 - Latest stable baseline for this fork (tag: v0.6.1, upstream/fix_actions)

---

## How to Report Issues

- For issues specific to openmotor-vibes: Use this repository's issue tracker
- For issues in the original openMotor: Visit https://github.com/reilleya/openMotor/issues
- When reporting, clearly indicate whether the issue exists in upstream or is specific to vibes fork
