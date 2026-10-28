import re
from typing import Any, Dict, List, Optional
from app.schemas.change_detection import ChangeItem

def parse_k8s_memory(mem_str: str) -> float:
    if not isinstance(mem_str, str):
        return float(mem_str)
    
    mem_str = mem_str.strip()
    match = re.match(r"^(\d+)([A-Za-z]+)?$", mem_str)
    if not match:
        return float(mem_str) if mem_str.isdigit() else 0.0
        
    value = float(match.group(1))
    unit = match.group(2)
    
    if not unit:
        return value
        
    unit = unit.lower()
    if unit in ["ki", "k"]:
        return value * 1024
    elif unit in ["mi", "m"]:
        return value * 1024**2
    elif unit in ["gi", "g"]:
        return value * 1024**3
    elif unit in ["ti", "t"]:
        return value * 1024**4
    
    return value

def parse_k8s_cpu(cpu_str: str) -> float:
    if not isinstance(cpu_str, str):
        return float(cpu_str)
        
    cpu_str = cpu_str.strip()
    if cpu_str.endswith("m"):
        return float(cpu_str[:-1]) / 1000.0
    return float(cpu_str)


class ChangeDetector:
    def __init__(self):
        pass

    def compare(self, old_config: Any, new_config: Any) -> List[ChangeItem]:
        import yaml
        
        if isinstance(old_config, str):
            old_config = yaml.safe_load(old_config) if old_config.strip() else {}
        if isinstance(new_config, str):
            new_config = yaml.safe_load(new_config) if new_config.strip() else {}
            
        old_config = old_config or {}
        new_config = new_config or {}
        
        changes = []
        self._compare_dicts(old_config, new_config, "", changes)
        return changes

    def _compare_dicts(self, old: Dict[str, Any], new: Dict[str, Any], current_path: str, changes: List[ChangeItem]):
        old_keys = set(old.keys()) if isinstance(old, dict) else set()
        new_keys = set(new.keys()) if isinstance(new, dict) else set()

        # Check for removed keys
        for key in old_keys - new_keys:
            path = f"{current_path}.{key}" if current_path else key
            changes.append(ChangeItem(
                type="REMOVED",
                path=path,
                old=old[key],
                new=None
            ))

        # Check for added keys
        for key in new_keys - old_keys:
            path = f"{current_path}.{key}" if current_path else key
            changes.append(ChangeItem(
                type="ADDED",
                path=path,
                old=None,
                new=new[key]
            ))

        # Check for modified keys
        for key in old_keys.intersection(new_keys):
            path = f"{current_path}.{key}" if current_path else key
            old_val = old[key]
            new_val = new[key]

            if isinstance(old_val, dict) and isinstance(new_val, dict):
                self._compare_dicts(old_val, new_val, path, changes)
            elif isinstance(old_val, list) and isinstance(new_val, list):
                # Simple list by index comparison
                min_len = min(len(old_val), len(new_val))
                for i in range(min_len):
                    list_path = f"{path}.{i}"
                    if isinstance(old_val[i], dict) and isinstance(new_val[i], dict):
                        self._compare_dicts(old_val[i], new_val[i], list_path, changes)
                    elif old_val[i] != new_val[i]:
                        change_type = self._determine_semantic_type(str(i), list_path, old_val[i], new_val[i])
                        changes.append(ChangeItem(type=change_type, path=list_path, old=old_val[i], new=new_val[i]))
                
                # Handle removed list items
                for i in range(min_len, len(old_val)):
                    changes.append(ChangeItem(type="REMOVED", path=f"{path}.{i}", old=old_val[i], new=None))
                
                # Handle added list items
                for i in range(min_len, len(new_val)):
                    changes.append(ChangeItem(type="ADDED", path=f"{path}.{i}", old=None, new=new_val[i]))
            elif old_val != new_val:
                change_type = self._determine_semantic_type(key, path, old_val, new_val)
                changes.append(ChangeItem(
                    type=change_type,
                    path=path,
                    old=old_val,
                    new=new_val
                ))

    def _determine_semantic_type(self, key: str, path: str, old_val: Any, new_val: Any) -> str:
        key_lower = key.lower()
        
        # Replica checks
        if "replica" in key_lower:
            try:
                if int(new_val) < int(old_val):
                    return "REPLICA_REDUCTION"
                elif int(new_val) > int(old_val):
                    return "REPLICA_INCREASE"
            except (ValueError, TypeError):
                pass
                
        # Memory checks
        if "memory" in key_lower:
            try:
                old_mem = parse_k8s_memory(str(old_val))
                new_mem = parse_k8s_memory(str(new_val))
                if new_mem < old_mem:
                    return "MEMORY_REDUCTION"
                elif new_mem > old_mem:
                    return "MEMORY_INCREASE"
            except (ValueError, TypeError):
                pass

        # CPU checks
        if "cpu" in key_lower:
            try:
                old_cpu = parse_k8s_cpu(str(old_val))
                new_cpu = parse_k8s_cpu(str(new_val))
                if new_cpu < old_cpu:
                    return "CPU_REDUCTION"
                elif new_cpu > old_cpu:
                    return "CPU_INCREASE"
            except (ValueError, TypeError):
                pass
                
        return "MODIFIED"
