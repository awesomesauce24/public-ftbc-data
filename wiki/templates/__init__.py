"""Template loading and management"""

from pathlib import Path
import json
import re


class TemplateLoader:
    """Load and render templates"""
    
    TEMPLATES_PATH = Path(__file__).parent
    
    @classmethod
    def load_realm_template(cls) -> dict:
        """Load realm JSON template"""
        template_file = cls.TEMPLATES_PATH / "realm.json"
        if template_file.exists():
            return json.loads(template_file.read_text())
        return {}
    
    @classmethod
    def load_object_template(cls) -> dict:
        """Load object JSON template"""
        template_file = cls.TEMPLATES_PATH / "object.json"
        if template_file.exists():
            return json.loads(template_file.read_text())
        return {}
    
    @classmethod
    def render(cls, template: dict, **kwargs) -> dict:
        """Render template with variables (recursive)"""
        if isinstance(template, dict):
            return {k: cls.render(v, **kwargs) for k, v in template.items()}
        elif isinstance(template, list):
            return [cls.render(item, **kwargs) for item in template]
        elif isinstance(template, str):
            result = template
            for key, value in kwargs.items():
                placeholder = "{{" + key + "}}"
                result = result.replace(placeholder, str(value) if value else "")
            return result
        return template
    
    @classmethod
    def render_conditional(cls, template: dict, **kwargs) -> dict:
        """Render template with conditional blocks"""
        import copy
        result = copy.deepcopy(template)
        
        # First render variables
        result = cls.render(result, **kwargs)
        
        # Then process conditionals
        result = cls._process_conditionals(result, kwargs)
        
        return result
    
    @classmethod
    def _process_conditionals(cls, obj, kwargs):
        """Recursively process conditional blocks"""
        if isinstance(obj, dict):
            return {k: cls._process_conditionals(v, kwargs) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls._process_conditionals(item, kwargs) for item in obj]
        elif isinstance(obj, str):
            # Process {{#if VAR}}...{{/if}} conditionals
            pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
            
            def replace_conditional(match):
                var_name = match.group(1)
                block_content = match.group(2)
                
                if var_name in kwargs and kwargs[var_name]:
                    return block_content
                return ""
            
            return re.sub(pattern, replace_conditional, obj, flags=re.DOTALL)
        
        return obj
