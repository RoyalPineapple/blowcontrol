# Dyson2MQTT Modular App Game Plan

> **Note to agents:**
> Please check off each item as you complete it. Update this file regularly to reflect progress and any changes to the plan.

## Project Goals
- Build a modular, maintainable, and testable Dyson controller app.
- Follow Python industry best practices (type hints, logging, config, no global state, etc.).
- Use a clean directory structure and clear separation of concerns.
- Support both synchronous and asynchronous operations.
- Provide machine-readable JSON output for automation.

---

## Checklist

- [x] 1. **Project Structure**
    - [x] Create directories: `commands/`, `mqtt/`, `state/`, `utils/`
    - [x] Add `__init__.py` to each module
    - [x] Add `main.py` and `cli.py` as entry points
- [x] 2. **Configuration Management**
    - [x] Implement config loading from environment variables and/or config file
    - [x] Document required configuration in README
- [x] 3. **MQTT Client Module**
    - [x] Implement a reusable MQTT client class
    - [x] Add topic helpers
    - [x] Add async wrapper for non-blocking operations
    - [x] Implement proper client ID management to prevent conflicts
- [x] 4. **Device State Management**
    - [x] Implement device state model and parsing
    - [x] Implement state parsing from MQTT messages
    - [x] Add pretty-printing for human consumption
    - [x] Add JSON output for machine consumption
    - [x] Implement thread-safe background state listener
- [x] 5. **Command Modules**
    - [x] Implement power command
    - [x] Implement fan speed command
    - [x] Implement auto mode command
    - [x] Implement night mode command
    - [x] Implement sleep timer command
    - [x] Implement clear sleep timer command
    - [x] Add generic command sending infrastructure
- [x] 6. **CLI Interface**
    - [x] Implement CLI using `argparse` for all device control commands
    - [x] Add real-time listening command (`listen`)
    - [x] Add on-demand state fetching (`get-state`)
    - [x] Add fire-and-forget state request (`request-state`)
    - [x] Add background listener with duration (`listen-bg`)
    - [x] Add async state fetching with JSON support (`async-get-state`)
    - [x] Implement `--json` flag for machine-readable output
- [x] 7. **Logging**
    - [x] Set up logging module for all output
    - [x] Add configurable log levels (quiet mode for JSON)
- [x] 8. **Async Operations**
    - [x] Implement async wrapper using `asyncio.to_thread()`
    - [x] Add clean async state fetching
    - [x] Support both verbose and quiet (JSON) modes
- [x] 9. **Testing**
    - [x] Add unit tests for power command
    - [x] Add unit tests for sleep timer commands
    - [x] Test all CLI commands for functionality
    - [x] Test async operations and JSON output
- [x] 10. **Documentation**
    - [x] Add docstrings to all modules and functions
    - [x] Write comprehensive README with usage instructions
    - [x] Document all CLI commands and options
    - [x] Add automation and scripting examples
    - [x] Document JSON output format
    - [x] Add troubleshooting guide
- [x] 11. **Security & Best Practices**
    - [x] Ensure no secrets are hardcoded or committed
    - [x] Use `subprocess.run` safely (if needed)
    - [x] Avoid global mutable state
    - [x] Implement proper error handling
    - [x] Use unique MQTT client IDs to prevent conflicts

---

## Completed Features

✅ **Core Device Control**
- Power on/off
- Fan speed control (1-10)
- Auto mode toggle
- Night mode toggle
- Sleep timer (set/clear)

✅ **State Monitoring**
- Real-time message listening
- On-demand state fetching
- Background listeners with timeout
- Thread-safe state management

✅ **Async Operations**
- Non-blocking state fetching
- Clean async/await interface
- Proper error handling

✅ **Machine-Readable Output**
- JSON output mode with `--json` flag
- Structured error responses
- Clean output for automation

✅ **Professional CLI**
- Comprehensive help system
- Consistent command patterns
- Clean, readable output
- Proper exit codes

---

## Architecture Highlights

- **Modular Design**: Each command is a separate module
- **Clean Separation**: MQTT, state, and CLI logic are separate
- **Async Support**: Uses `asyncio.to_thread()` for clean async operations
- **Thread Safety**: Background listeners use proper synchronization
- **Error Handling**: Comprehensive error handling with structured responses
- **Configuration**: Environment-based config with `.env` support

---

## Future Enhancements (Optional)

- [ ] **Additional Commands**
    - [ ] Oscillation control (if device supports)
    - [ ] Temperature control (for heating models)
    - [ ] Filter status and replacement alerts

- [ ] **Advanced Features**
    - [ ] Scheduling system for automated control
    - [ ] Integration with home automation systems
    - [ ] Web API wrapper
    - [ ] Configuration validation and setup wizard

- [ ] **Testing & Quality**
    - [ ] Integration tests with mock MQTT broker
    - [ ] Performance benchmarks
    - [ ] Code coverage reporting

---

## Notes

- **All core functionality is complete** and working reliably
- **Async operations** provide clean, non-blocking state access
- **JSON output** enables easy integration with other systems
- **Thread-safe design** allows multiple concurrent operations
- **Professional CLI** with comprehensive help and error handling
- **Modular architecture** makes extending the system straightforward

The app is production-ready for controlling Dyson devices via MQTT with both interactive and programmatic interfaces.
