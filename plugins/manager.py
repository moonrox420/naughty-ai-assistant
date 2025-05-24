import os
import importlib.util

def load_plugin(plugin_name):
    """Load a plugin from the plugins directory."""
    try:
        plugin_path = os.path.join("plugins", f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            return f"Plugin {plugin_name} not found."

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        return f"Error loading plugin {plugin_name}: {str(e)}"

def execute_plugin(plugin_name, function_name, *args, **kwargs):
    """Execute a function from a loaded plugin."""
    try:
        plugin = load_plugin(plugin_name)
        if isinstance(plugin, str):
            return plugin  # Error message
        func = getattr(plugin, function_name, None)
        if not func:
            return f"Function {function_name} not found in plugin {plugin_name}."
        return func(*args, **kwargs)
    except Exception as e:
        return f"Error executing plugin {plugin_name}: {str(e)}"
