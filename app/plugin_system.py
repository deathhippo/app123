# app/plugin_system.py
import importlib
import json
import os
from typing import Dict, Any


def _read_state(app) -> Dict[str, Any]:
    path = app.config['PLUGINS_STATE_FILE']
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _write_state(app, state: Dict[str, Any]) -> None:
    path = app.config['PLUGINS_STATE_FILE']
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _discover_packages(app) -> Dict[str, str]:
    """
    Returns {plugin_name: module_path}, scanning app/plugins/* packages that have __init__.py
    """
    base_dir = app.config['PLUGINS_DIR']
    results: Dict[str, str] = {}
    if not os.path.isdir(base_dir):
        return results
    for entry in os.listdir(base_dir):
        full = os.path.join(base_dir, entry)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, '__init__.py')):
            results[entry] = f"app.plugins.{entry}"
    return results


def get_installed_plugins(app) -> Dict[str, Dict[str, Any]]:
    """
    Returns metadata for all discovered plugins:
      {
        name: {
          "enabled": bool,
          "module": "app.plugins.name",
          "meta": {.}  # PLUGIN_META if provided
        }, .
      }
    """
    discovered = _discover_packages(app)
    state = _read_state(app)
    out: Dict[str, Dict[str, Any]] = {}
    for name, modpath in discovered.items():
        enabled = bool(state.get(name, {}).get("enabled", False))
        meta = {}
        try:
            mod = importlib.import_module(modpath)
            meta = getattr(mod, "PLUGIN_META", {}) or {}
        except Exception:
            # Do not fail listing if a plugin has import issues
            pass
        out[name] = {"enabled": enabled, "module": modpath, "meta": meta}
    return out


def set_plugin_enabled(app, name: str, enabled: bool) -> Dict[str, Any]:
    state = _read_state(app)
    state[name] = state.get(name, {})
    state[name]["enabled"] = bool(enabled)
    _write_state(app, state)
    return state[name]


def load_plugins(app) -> None:
    """
    Imports and registers all ENABLED plugins.
    Each plugin package can export: PLUGIN_META, and def register(app) -> dict
    The register() function is expected to call app.register_blueprint(...) internally,
    and may return metadata to record.
    """
    if "loaded_plugins" not in app.extensions:
        app.extensions["loaded_plugins"] = {}
    loaded = app.extensions["loaded_plugins"]

    for name, info in get_installed_plugins(app).items():
        if not info["enabled"]:
            continue
        if name in loaded:
            continue  # already loaded

        try:
            mod = importlib.import_module(info["module"])
            register = getattr(mod, "register", None)
            if callable(register):
                result = register(app) or {}
            else:
                result = {}
            loaded[name] = {"module": info["module"], "meta": info.get("meta", {}), "register_result": result}
            print(f"[plugins] loaded '{name}' from {info['module']}")
        except Exception as e:
            print(f"[plugins] FAILED to load '{name}': {e}")


def reload_plugins(app) -> None:
    """
    Loads newly enabled plugins that aren't loaded yet.
    (Disabling an already-loaded plugin will take effect on next restart.)
    """
    load_plugins(app)
