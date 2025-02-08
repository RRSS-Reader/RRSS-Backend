The **RRSS Config Management System** is designed to enable developers to efficiently manage and retrieve configurations for both the RRSS platform and its associated plugins.

# Structure

[![image](https://github.com/user-attachments/assets/db581be7-6ad0-48c9-8c92-51bb5bae69f5)](https://excalidraw.com/#json=KAF0STPV7HUf13lTiXyS_,c9pNwgGBHEogId9c4UMhKg)

The image above shows the basic structure of RRSS Config Management System.

- ConfigManager
- ConfigProvider

---

**`ConfigManager`** will serve as a global configuration manager, instantiated as a class. Its responsibilities include:

- **Handling configuration-related requests** _(e.g., add, remove, get, etc.)_ from clients _(RRSS, plugins, etc.)_.
- Managing all `ConfigProvider` instances _(e.g., adding, removing, etc.)_.
- Implementing basic request cache control.

---

**`ConfigProvider`** is responsible for:

- Retrieving actual configuration data from various sources _(e.g., databases, JSON files, environment variables, etc.)_.
- Handling detailed cache control, source authentication, logging, and other related tasks.

# Configuration Provider

- CachedProvider
- AttrProvider
- JSONProvider
- DictProvider
