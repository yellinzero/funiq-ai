from typing import Any, Dict

from loguru import logger


class ConvertHandlingMixin:
    """Mixin class for handling config conversions."""

    def convert_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert config values according to config schema types.

        Args:
            config: Configuration dictionary with rendered values

        Returns:
            Configuration with correct data types

        Raises:
            ValueError: If conversion fails or schema validation fails
            TypeError: If input types are incorrect
        """
        if not hasattr(self, "config_schema") or not self.config_schema:
            logger.warning("No config schema defined, skipping conversion")
            return config

        try:
            return self._convert_by_schema(data=config, schema=self.config_schema)
        except (ValueError, TypeError) as e:
            logger.error(f"Config conversion failed: {e!s}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during config conversion: {e!s}")
            raise ValueError(f"Failed to convert config: {e!s}") from e

    def _convert_by_schema(self, data: Any, schema: dict[str, Any]) -> Any:
        """Recursively convert data according to schema definition.

        Args:
            data: The data to convert
            schema: The JSON schema defining the expected types

        Returns:
            Converted data matching schema types

        Raises:
            ValueError: If conversion fails
            TypeError: If input types are incorrect
        """
        if not schema or 'type' not in schema:
            return data

        try:
            schema_type = schema['type']
            
            # Handle null values
            if data is None:
                if "null" in schema_type or schema_type == "null":
                    return None
                raise ValueError(f"Null value not allowed for type {schema_type}")

            # Handle object type
            if schema_type == "object" and isinstance(data, dict):
                if 'properties' not in schema:
                    return data
                return {
                    key: self._convert_by_schema(value, schema['properties'].get(key, {}))
                    for key, value in data.items()
                    if key in schema['properties']
                }

            # Handle array type
            if schema_type == "array" and isinstance(data, list):
                if 'items' not in schema:
                    return data
                return [self._convert_by_schema(item, schema['items']) for item in data]

            # Handle primitive types
            if schema_type == "integer":
                try:
                    return int(data)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Cannot convert '{data}' to integer") from e

            if schema_type == "number":
                try:
                    return float(data)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Cannot convert '{data}' to number") from e

            if schema_type == "boolean":
                if isinstance(data, str):
                    if data.lower() in ("true", "1", "yes", "on"):
                        return True
                    if data.lower() in ("false", "0", "no", "off"):
                        return False
                    raise ValueError(f"Cannot convert string '{data}' to boolean")
                return bool(data)

            if schema_type == "string":
                return str(data)

            # Handle union types
            if isinstance(schema_type, list):
                errors = []
                for type_name in schema_type:
                    try:
                        temp_schema = {
                            "type": type_name
                        }
                        return self._convert_by_schema(data, temp_schema)
                    except Exception as e:
                        errors.append(f"{type_name}: {e!s}")
                raise ValueError(
                    f"Could not convert '{data}' to any of types {schema_type}. Errors: {'; '.join(errors)}"
                )

            return data

        except (ValueError, TypeError) as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to convert '{data}' according to schema: {e!s}") from e
