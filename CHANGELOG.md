# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Development tooling configuration
- Comprehensive contributing guidelines
- Code coverage reporting
- Security analysis with bandit and safety
- Type checking with mypy

### Changed
- Improved test mocking system for CI compatibility
- Enhanced CLI error handling and validation
- Updated configuration validation logic
- Better test isolation and reliability

### Fixed
- Tests no longer connect to real devices during CI
- Fixed mock application issues in integration tests
- Resolved configuration test failures
- Improved CLI error handling and exit codes
- Fixed DeviceStatePrinter method calls

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Dyson2MQTT
- CLI interface for Dyson fan control
- MQTT client for device communication
- Support for power, speed, auto mode, night mode, and sleep timer
- Oscillation control (width, direction, stop)
- Real-time state monitoring
- JSON output for automation
- Async operations support
- Comprehensive test suite
- Configuration management with environment variables

### Features
- **Device Control**: Power, fan speed, auto mode, night mode, sleep timer
- **State Monitoring**: Real-time listening, on-demand state fetching
- **Async Support**: Non-blocking operations with async/await
- **JSON Output**: Machine-readable responses for automation
- **Thread-Safe**: Background listeners with proper synchronization
- **Professional CLI**: Clean interface with helpful output

---

## Version History

- **1.0.0**: Initial release with core functionality
- **Unreleased**: CI/CD improvements and development tooling
