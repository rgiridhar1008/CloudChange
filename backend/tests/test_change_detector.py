import pytest
from app.modules.change_detection.detector import ChangeDetector

def test_no_change():
    detector = ChangeDetector()
    old_config = {"replicaCount": 3, "memory": "512Mi"}
    new_config = {"replicaCount": 3, "memory": "512Mi"}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 0

def test_replica_increase():
    detector = ChangeDetector()
    old_config = {"replicaCount": 1}
    new_config = {"replicaCount": 3}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "REPLICA_INCREASE"
    assert changes[0].path == "replicaCount"
    assert changes[0].old == 1
    assert changes[0].new == 3

def test_replica_reduction():
    detector = ChangeDetector()
    old_config = {"replicaCount": 3}
    new_config = {"replicaCount": 1}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "REPLICA_REDUCTION"

def test_memory_change():
    detector = ChangeDetector()
    old_config = {"resources": {"requests": {"memory": "512Mi"}}}
    new_config = {"resources": {"requests": {"memory": "128Mi"}}}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "MEMORY_REDUCTION"
    assert changes[0].path == "resources.requests.memory"
    
    # Test memory increase
    new_config2 = {"resources": {"requests": {"memory": "1Gi"}}}
    changes2 = detector.compare(old_config, new_config2)
    assert len(changes2) == 1
    assert changes2[0].type == "MEMORY_INCREASE"

def test_cpu_change():
    detector = ChangeDetector()
    old_config = {"cpu": "100m"}
    new_config = {"cpu": "200m"}
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "CPU_INCREASE"

def test_new_resource():
    detector = ChangeDetector()
    old_config = {"replicaCount": 3}
    new_config = {"replicaCount": 3, "livenessProbe": {"path": "/health"}}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "ADDED"
    assert changes[0].path == "livenessProbe"
    assert changes[0].new == {"path": "/health"}

def test_deleted_resource():
    detector = ChangeDetector()
    old_config = {"replicaCount": 3, "livenessProbe": {"path": "/health"}}
    new_config = {"replicaCount": 3}
    
    changes = detector.compare(old_config, new_config)
    assert len(changes) == 1
    assert changes[0].type == "REMOVED"
    assert changes[0].path == "livenessProbe"

def test_multiple_changes():
    detector = ChangeDetector()
    old_config = {
        "services": {
            "order": {
                "replicaCount": 3,
                "memory": "512Mi",
                "old_key": "exists"
            }
        }
    }
    new_config = {
        "services": {
            "order": {
                "replicaCount": 1,
                "memory": "1Gi",
                "new_key": "added"
            }
        }
    }
    
    changes = detector.compare(old_config, new_config)
    
    # We expect 4 changes: REPLICA_REDUCTION, MEMORY_INCREASE, REMOVED (old_key), ADDED (new_key)
    assert len(changes) == 4
    
    types = [c.type for c in changes]
    assert "REPLICA_REDUCTION" in types
    assert "MEMORY_INCREASE" in types
    assert "REMOVED" in types
    assert "ADDED" in types
