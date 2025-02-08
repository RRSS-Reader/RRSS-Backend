_Translation Provider_ is used to provide translation resources for front end UI interface
using `i18next` project.

# Structure

When we talking about _frontend_ and _backend_ of RRSS translation system:

- **Frontend**: Fetch translation resources from backend, then properly display the translation result to user.
- **Backend**: Manage translation resources, provide endpoints for frontend to retrieve corresponding resources.

## Frontend

Frontend should use package [i18next](https://www.i18next.com/) as the frontend translation framework.

Additionally, `i18next-fetch-backend` could be used to retrieve translation resources from backend endpoints.

## Backend

A global Translation Manager _(powered by `tranlation.manager._TranslationResourceManager`)_ is provided to allow RRSS or other plugins to register new translation resources. This manager is also responsible for loading and caching the corresponding resources when needed.

## Diagram

The overall translation system structure is shown in the diagram below:

[![](https://github.com/user-attachments/assets/a0197f4a-7dee-497e-a91d-3f4b9d23de20)](https://excalidraw.com/#json=vdgrFF_Fzm7XQJRT1_PQt,s5uenLyyQKTEKkhUtSgXsQ)

# Backend Resources Registration

## Access Manager Instance

To directly access translation manager instance, you could:

```python
from translation.manager import instance as trans_mgr
trans_mgr.register(...)
```

## Manually Register Resources

> This approach is not recommended, the "Scan Locale Directory" method should be used in most cases,
> which would be introduced below.

A new `TransResourceMetaData` instance should be created before adding to the manager.

```python
new_resource = TransResourceMetaData(lng=..., ns=..., location=...)
```

Check out type annotations and docstrings of `TransResourceMetaData` for more info.

To manually register a new translation resource, you could use `register()` method of manager instance:

```
resource = TransResourceMetaData(lng="en-US", ns="common", location=Traversable())
trans_mgr.register(resource)
```

> Check out docstring of `register()` for more info.

## Scan Locale Directory

In most cases, all relevant translation resources is organized in a locale directory,
which should have the following structure:

```plaintext
[lng_code]/
└── [namespace].json
```

Following is a possible locale directory structure for a plugin called `my_rrss_plugin`:

```plaintext
en-US/
├── my_rrss_plugin__common.json
└── my_rrss_plugin__custom_errs.json
de/
├── my_rrss_plugin__common.json
└── my_rrss_plugin__custom_errs.json
```

`discover()` method could be used to scan and add all translation resources in a locale folder to the manager
as long as the location of locale directory is known.

```python
trans_mgr.discover(anchor=".assets.locale")
trans_mgr.discover(anchor=".assets.locale", add_to_res=False)  # will only return list of res, do not add to mgr instance
```

> The parameter `anchor` should direclty point to the location of locale directory, and will be passed to `importlib.resources.files()`

### Details

Translation Manager use `importlib.resources` internally to manage translation resources.

- [importlib.resources.Anchor](https://docs.python.org/3/library/importlib.resources.html#importlib.resources.Anchor)
- [importlib.resources.files()](https://docs.python.org/3/library/importlib.resources.html#importlib.resources.files)

# Get Resources

> You could skip reading this part **if you only cares how to register(add) new translation resources**, e.g.: You are developing a RRSS plugin and need to provide i18n for this plugin.

Use `get_resource_json()` to retrieve registered resources.

```python
json_str: str = get_resource_json(lng="en", ns="some_namespace")
```
