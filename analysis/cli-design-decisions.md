# CLI and Configuration Design Decisions

**Created:** 2026-06-05
**Status:** Approved
**Version:** 1.0

---

## Overview

This document summarizes the key design decisions for baseweb's CLI and configuration system, including the rationale and trade-offs considered for each decision.

---

## Decision 1: Clevis as Configuration Loading Mechanism

### Decision

Use **Clevis** as the primary configuration loading mechanism for baseweb.

### Rationale

1. **Mature and Tested**: Clevis is a well-established configuration system with proven reliability
2. **Layered Configuration**: Built-in support for priority-based configuration (defaults < user < project < env < CLI)
3. **Automatic Environment Variable Handling**: No manual code needed to map environment variables to config fields
4. **Type-Safe Dataclass Population**: Configuration is loaded directly into typed dataclasses with validation
5. **CLI Argument Generation**: Clevis can generate CLI arguments from the config schema automatically

### Trade-offs

**Pros:**
- Reduces implementation complexity significantly
- Leverages existing, tested code
- Benefits from Clevis updates and improvements
- Consistent with other projects using Clevis

**Cons:**
- Adds Clevis as a dependency
- Less control over configuration loading details
- Must conform to Clevis conventions and naming
- Learning curve for developers unfamiliar with Clevis

### Alternatives Considered

1. **Manual TOML Parsing + Environment Variable Handling**
   - More code to maintain
   - More potential for bugs
   - Reinventing existing solutions
   - No automatic CLI argument generation

2. **dynaconf**
   - Heavier dependency
   - More complex configuration system
   - Overkill for baseweb's needs

3. **python-dotenv**
   - Only handles .env files
   - No layered configuration
   - No TOML support

### Outcome

Clevis chosen for its balance of simplicity, features, and maintainability.

---

## Decision 2: BasewebConfig as Single Source of Truth

### Decision

Define all application and server configuration in a single `BasewebConfig` dataclass, which serves as the single source of truth for all configuration.

### Rationale

1. **Centralized Configuration**: All settings in one place, easy to find and modify
2. **Type Safety**: Dataclass provides type hints and IDE autocomplete
3. **Documentation**: Schema serves as living documentation
4. **Validation**: Type hints enable runtime validation
5. **Immutability**: Dataclasses can be made frozen for immutable configuration

### Trade-offs

**Pros:**
- Clear, single location for all configuration
- IDE support for autocomplete and type checking
- Easy to validate and reason about
- Can be serialized/deserialized

**Cons:**
- Large dataclass with many fields
- Must import dataclass to create programmatically
- Changes to config require updating the dataclass
- Nested configuration (GunicornConfig) adds complexity

### Alternatives Considered

1. **Multiple Configuration Classes**
   - Separates app config from server config
   - More classes to manage
   - Harder to pass around

2. **Dictionary-Based Configuration**
   - More flexible, no schema
   - Loses type safety
   - No IDE autocomplete
   - Harder to validate

3. **Configuration Files Only**
   - No programmatic configuration
   - Loses flexibility for testing and dynamic configuration
   - Harder to create in code

### Outcome

Single BasewebConfig dataclass chosen for clarity and type safety.

---

## Decision 3: No Backward Compatibility

### Decision

This is a **breaking change**. The new configuration system uses BasewebConfig dataclasses populated by Clevis. The old environment variable and settings dict approach is no longer supported.

### Rationale

1. **Clean Architecture**: Removes legacy code and complexity
2. **Single Approach**: Avoids confusion between old and new approaches
3. **Simpler Implementation**: No need to maintain compatibility layer
4. **Easier Testing**: One code path to test
5. **Clear Migration Path**: Users know exactly what to change

### Trade-offs

**Pros:**
- Simpler, cleaner codebase
- Easier to maintain and test
- No technical debt from compatibility layer
- Clear, unambiguous design

**Cons:**
- Breaking change for existing users
- Requires migration effort from users
- May frustrate users with working setups
- Needs clear communication and documentation

### Mitigation

1. **Version Bump**: Major version bump to indicate breaking change
2. **Migration Guide**: Clear, step-by-step migration guide
3. **Release Notes**: Prominent breaking changes section
4. **Deprecation Period**: Consider deprecation warnings before removal (not implemented)
5. **Example Migration**: Provide before/after examples

### Alternatives Considered

1. **Full Backward Compatibility**
   - Support both old and new approaches
   - Adds significant complexity
   - Confuses users about which approach to use
   - Technical debt from maintaining dual code paths

2. **Deprecation Period**
   - Keep old approach working with warnings
   - Still requires supporting both code paths
   - Delays clean architecture

3. **Compatibility Layer**
   - Translate old settings dict to new config
   - Adds code complexity
   - Risk of subtle bugs in translation

### Outcome

Clean break chosen for architectural clarity, with strong migration support.

---

## Decision 4: `check` Command for Configuration Validation

### Decision

Add a `baseweb check` command that validates the configuration without running the application.

### Rationale

1. **Fail Fast**: Catch configuration errors before trying to run
2. **Clear Error Messages**: Provide actionable error messages
3. **CI/CD Integration**: Validate configuration in deployment pipelines
4. **Debugging Tool**: Help users debug configuration problems
5. **Documentation**: Command serves as implicit documentation

### Trade-offs

**Pros:**
- Early error detection
- Useful for automation
- Helps users debug issues
- Low maintenance (reuses validation logic)

**Cons:**
- Additional command to maintain
- May duplicate some validation logic
- Adds to CLI complexity

### Alternatives Considered

1. **Validate Only on `serve`**
   - Errors discovered only when trying to run
   - Less useful for CI/CD
   - Harder to debug in production

2. **Separate Validation Script**
   - More files to maintain
   - Not integrated with baseweb CLI
   - Harder to discover

3. **Configuration File Validator**
   - External tool
   - Not integrated with baseweb
   - May get out of sync

### Outcome

`check` command added to CLI for validation before running.

---

## Decision 5: Baseweb.__init__ Accepts BasewebConfig Directly

### Decision

The Baseweb class constructor accepts a BasewebConfig instance directly, not a settings dict.

### Rationale

1. **Type Safety**: IDE and type checker know what's expected
2. **Single Source of Truth**: No translation between config and settings
3. **Clear Contract**: Explicit about what configuration is needed
4. **Avoids Dict Hell**: No nested dict structures to navigate
5. **Encourages Good Practices**: Users create config objects, not dicts

### Trade-offs

**Pros:**
- Clear, explicit type
- IDE autocomplete
- Validation in dataclass
- Immutable configuration

**Cons:**
- Users must import BasewebConfig
- More verbose than dict
- Can't use **kwargs for configuration

### Alternatives Considered

1. **Accept Both BasewebConfig and Dict**
   - More flexible for users
   - Adds complexity and translation logic
   - Loses type safety for dict path

2. **Accept **kwargs**
   - Very flexible
   - No type safety
   - No validation
   - Harder to document

3. **Keep Settings Dict**
   - Backward compatible
   - No type safety
   - Encourages bad practices

### Outcome

Baseweb.__init__ accepts BasewebConfig directly for clarity and type safety.

---

## Decision 6: All Configuration in BasewebConfig

### Decision

All application settings and server configuration are stored in BasewebConfig, including Gunicorn settings.

### Rationale

1. **Unified Configuration**: One place to find all settings
2. **Single File**: All configuration in baseweb.toml
3. **Environment Variables**: Clevis handles all env var mapping
4. **Type Safety**: All settings have type hints
5. **Documentation**: Single schema to document

### Trade-offs

**Pros:**
- Single source of truth
- Easy to find all configuration
- Consistent approach for all settings
- Single TOML file

**Cons:**
- Large configuration object
- Mixes app and server concerns
- May include settings not needed in all contexts

### Alternatives Considered

1. **Separate GunicornConfig File**
   - Server settings in separate file
   - More files to manage
   - Harder to see full picture

2. **Environment Variables Only for Server**
   - Server settings not in TOML
   - Inconsistent with app settings
   - Loses benefits of Clevis

3. **Multiple Configuration Files**
   - App config, server config, etc.
   - Complex to manage
   - Hard to understand precedence

### Outcome

All configuration in BasewebConfig for simplicity and consistency.

---

## Decision 7: TOML Configuration Structure with Nested Sections

### Decision

Use a TOML configuration structure with nested sections for logical grouping, keeping `[server]` as a nested section and supporting application-specific configurations via `register_app_config()`.

### Rationale

1. **Organization**: Nested sections group related settings logically (branding, features, server)
2. **Clarity**: Clear separation of concerns between app, server, and feature configuration
3. **Extensibility**: Application-specific config via `register_app_config()` allows apps to extend without modifying baseweb
4. **Validation**: Nested structure enables context-aware validation (e.g., `icons_dir` required when `style = "pwa"`)
5. **Future-Proof**: Plugin namespace reserved for future extensibility

### Structure

**Root Level:**
- `app_uri`, `name`, `title`, `short_name`, `description`, `author`, `version` (optional)
- `url`, `main_template`, `style`

**Nested Sections:**
- `[branding.colors]` - Color scheme configuration
- `[branding.icons]` - Application and social icons
- `[branding.favicon]` - Favicon settings
- `[features.socketio]` - WebSocket configuration
- `[features.pwa]` - Progressive Web App settings
- `[server]` - Gunicorn server configuration
- `[app.**]` - Application-specific (registered via `register_app_config()`)
- `[plugin.**]` - Plugin configurations (future)

### Key Design Choices

1. **`[server]` stays nested** - Maintains clear separation between server and app configuration
2. **`register_app_config(AppConfig)` pattern** - Allows apps to define custom config sections
3. **`icons_dir` required when `style = "pwa"`** - Validation ensures PWA apps have required assets
4. **`version` is optional** - Not currently used by baseweb, but available for apps

### Environment Variable Interpolation

TOML files support environment variable interpolation using either `envtoml` or `tomlev` parser:

- `${VAR}` - Use environment variable
- `${VAR:-default}` - Use default if not set

### Trade-offs

**Pros:**
- Clear organization and structure
- Extensible for applications and plugins
- Type-safe configuration
- Environment variable interpolation support
- Context-aware validation

**Cons:**
- More complex than flat configuration
- Requires documentation for nested structure
- Applications must register custom config sections

### Implementation

```python
# Register application-specific configuration
from baseweb.config import register_app_config

@dataclass
class MyAppConfig:
    debug: bool = False
    custom_setting: str = "default"

register_app_config("myapp", MyAppConfig)
```

```toml
# Application-specific configuration in TOML
[app.myapp]
debug = false
custom_setting = "value"
```

### Outcome

Nested TOML structure chosen for organization, extensibility, and validation capabilities.

---

## Summary

These design decisions prioritize:

1. **Clarity**: Single source of truth, explicit types, clean architecture
2. **Simplicity**: Fewer code paths, mature dependencies, clear migration
3. **Type Safety**: Dataclasses, IDE support, validation
4. **Developer Experience**: Clear error messages, helpful CLI commands
5. **Extensibility**: Application-specific configuration via registration pattern

The trade-offs accepted are:

1. **Breaking Change**: No backward compatibility for architectural clarity
2. **Dependency**: Clevis added as a required dependency
3. **Verbosity**: Users must create config objects explicitly
4. **Complexity**: Nested TOML structure requires documentation

These decisions align with the overall goal of creating a maintainable, clear, and developer-friendly configuration system for baseweb.