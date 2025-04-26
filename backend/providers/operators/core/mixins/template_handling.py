from typing import Any, Dict, List

from jinja2 import Environment, nodes, select_autoescape
from loguru import logger


class TemplateHandlingMixin:
    """Mixin class for handling template rendering and variable path extraction."""
    
    _jinja_env: Environment
    _stream_node_ids: List[str]
    _config_value_paths_map: Dict[str, List[str]]
    
    def _init_jinja_env(self):
        # Initialize Jinja2 environment
        self._jinja_env = Environment(
            autoescape=select_autoescape(["html", "xml"]),
            keep_trailing_newline=True,
            # Add useful built-in functions and filters
            extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
            # Enable optimization
            optimized=True,
            # Configure flexible syntax
            variable_start_string="{{",
            variable_end_string="}}",
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters and global functions
        self._jinja_env.filters.update(
            {
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
            }
        )
        
    def _extract_config_value_paths_map(self, template_str: str) -> List[str]:
        """get template paths from template string

        Args:
            template_str: template string to analyze

        Returns:
            list of variable access paths
        """
        if not isinstance(template_str, str) or "{{" not in template_str:
            return []

        ast = self._jinja_env.parse(template_str)
        paths = set()  # use set to deduplicate

        def process_node(node):
            if isinstance(node, nodes.Name):
                paths.add(node.name)
            elif isinstance(node, nodes.Getattr):
                parts = []
                current = node
                while isinstance(current, nodes.Getattr):
                    parts.append(current.attr)
                    current = current.node
                if isinstance(current, nodes.Name):
                    parts.append(current.name)
                    paths.add('.'.join(parts[::-1]))

        # traverse top-level nodes
        for node in ast.body:
            if isinstance(node, nodes.Output):
                for n in node.nodes:
                    if isinstance(n, (nodes.Name, nodes.Getattr)):
                        process_node(n)

        return sorted(paths)
    
    def _filter_non_stream_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out config entries that reference stream inputs.
        
        Args:
            config: Original config dictionary
            
        Returns:
            Dict containing only non-stream config entries
        """
        if not self._stream_node_ids or len(self._stream_node_ids) == 0:
            return config

        non_stream_config = {}
        
        def _should_keep_path(paths: List[str]) -> bool:
            # check if any path is a stream node id
            return not any(path.split('.')[0] in self._stream_node_ids for path in paths)

        def _filter_recursive(src: Dict[str, Any], dest: Dict[str, Any], parent_path: str = ""):
            for key, value in src.items():
                current_path = f"{parent_path}.{key}" if parent_path else key
                
                if isinstance(value, dict):
                    dest[key] = {}
                    _filter_recursive(value, dest[key], current_path)
                    if not dest[key]:
                        del dest[key]
                elif isinstance(value, list):
                    filtered_list = []
                    for i, item in enumerate(value):
                        list_path = f"{current_path}[{i}]"
                        if isinstance(item, dict):
                            new_dict = {}
                            _filter_recursive(item, new_dict, list_path)
                            if new_dict:
                                filtered_list.append(new_dict)
                        elif isinstance(item, str):
                            paths = self._config_value_paths_map.get(list_path, [])
                            if not paths or _should_keep_path(paths):
                                filtered_list.append(item)
                        else:
                            filtered_list.append(item)
                    if filtered_list:
                        dest[key] = filtered_list
                elif isinstance(value, str):
                    paths = self._config_value_paths_map.get(current_path, [])
                    if not paths or _should_keep_path(paths):
                        dest[key] = value
                else:
                    dest[key] = value
        _filter_recursive(src=config, dest=non_stream_config)
        return non_stream_config

    def _analyze_config_paths(self, config: Dict[str, Any]) -> None:
        """analyze all template variable paths in config and store in instance

        Args:
            config: config dictionary
        """
        self._config_value_paths_map = {}
        
        def _analyze_recursive(current_config: Dict[str, Any], prefix: str = ""):
            for key, value in current_config.items():
                current_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    _analyze_recursive(value, current_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            _analyze_recursive(item, f"{current_key}[{i}]")
                        elif isinstance(item, str):
                            paths = self._extract_config_value_paths_map(item)
                            if paths:
                                self._config_value_paths_map[f"{current_key}[{i}]"] = paths
                elif isinstance(value, str):
                    paths = self._extract_config_value_paths_map(value)
                    if paths:
                        self._config_value_paths_map[current_key] = paths

        _analyze_recursive(config)

    def _render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """render template string (only for non-stream scenario)

        Args:
            template_str: template string
            context: context dictionary

        Returns:
            rendered string
        """
        try:
            if "{{" not in template_str:
                return template_str

            template = self._jinja_env.from_string(template_str.strip())
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template '{template_str}': {e!s}")
            raise ValueError(f"Template rendering error: {e!s}") from e

    def _render_config(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """render config (only for non-stream scenario)

        Args:
            config: config dictionary
            context: context dictionary

        Returns:
            rendered config
        """
        rendered_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                rendered_config[key] = self._render_config(value, context)
            elif isinstance(value, list):
                rendered_config[key] = [
                    self._render_config(item, context)
                    if isinstance(item, dict)
                    else self._render_template(item, context)
                    for item in value
                ]
            else:
                rendered_config[key] = self._render_template(value, context)
        return rendered_config