# Registry Manager

The `reg_mgr` package is used as a Registry Manager for systems like `event` and `pipe`.

## Structure

- **`RegistryManager`**: Manages a collection of `RegisterableData`.
- **`RegistryGroupManager`**: Manages a group of `RegistryManager` instances.

### Examples

In the context of the RRSS Event system, the structure works as follows:

1. **Event Handlers**: Event handlers are subclasses of `RegisterableData`.
2. **Single Event Manager**: Each event is managed by a `SingleEventManager`, which is a subclass of `RegistryManager`. This manager is responsible for handling all event handlers related to that specific event.
3. **Event Manager**: The `EventManager` is a subclass of `RegistryGroupManager`. It manages all events, essentially managing a collection of `SingleEventManager` instances.

---

- **`EventManager`** (RegistryGroupManager) → Manages multiple `SingleEventManager` instances.
- **`SingleEventManager`** (RegistryManager) → Manages multiple event handlers (`RegisterableData`) for a specific event.
- **`Event Handler`** → Subclasses of `RegisterableData` that perform actions when an event is triggered.

Check out the diagram below:

```mermaid
graph TD

  A[EventManager] --->|Manages| B[SingleEventManager]
  B --->|Manages| C[Event Handler]
  B --->|Manages| G[Event Handler]
  A --->|Manages| D[SingleEventManager]
  D --->|Manages| E[Event Handler]
  D --->|Manages| F[Event Handler]

  RegistryGroupManager ---> RegistryManager
  RegistryManager ---> RegisterableData

  classDef eventManager fill:#f9f,stroke:#333,stroke-width:2px;
  classDef singleEventManager fill:#bbf,stroke:#333,stroke-width:2px;
  classDef eventHandler fill:#bfb,stroke:#333,stroke-width:2px;

  class A,RegistryGroupManager eventManager;
  class B,D,RegistryManager singleEventManager;
  class C,E,F,G,RegisterableData eventHandler;
```

## Using / Customizing

### RegisterableData

Your custom registerable data **must be derived from `RegisterableData`**, which serves as a basic data class containing essential fields.

However, you may need to **add new methods or fields based on your requirements**. For instance, in an event system, you might introduce a new method like `emit()`.

> Refer to the docstring of `RegisterableData` for more details, or check the implementation of `EventHandler` as an example.

### RegistryManager

In this package, **`RegistryManager` is defined as a Protocol**, allowing flexibility in its implementation.

You can create your own `RegistryManager` class based on your specific needs. However, some basic implementations are already provided:

- `ListRegistryManager`
- `PriorityListRegistryManager`

> Check the docstrings of these classes for more details.

### Custom Exceptions

# TODO
