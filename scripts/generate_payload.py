#!/usr/bin/env python3
import json
import sys
import subprocess

def main():
    # In a real scenario, this would use helm diff or git diff to parse changes
    # For now, we simulate a basic parser that looks at arguments
    resource_name = sys.argv[1] if len(sys.argv) > 1 else "payment-service"
    
    payload = {
        "changed_resource": resource_name,
        "changes": [
            {
                "type": "REPLICA_REDUCTION",
                "path": "spec.replicas",
                "old": 3,
                "new": 1
            }
        ]
    }
    
    with open("dynamic_payload.json", "w") as f:
        json.dump(payload, f)
        
    print("Generated dynamic_payload.json")

if __name__ == "__main__":
    main()
