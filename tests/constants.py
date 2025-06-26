# Constants for experiment IDs and drift IDs
PRIVATE_EXPS = ["00000000-0000-0001-0001-000000000001"]
PUBLIC_EXPS = ["00000000-0000-0001-0001-000000000002"]
EDITABLE_EXPS = [
    "00000000-0000-0001-0002-000000000001",
    "00000000-0000-0001-0002-000000000002",
    "00000000-0000-0001-0002-000000000003",
    "00000000-0000-0001-0002-000000000004",
]
UNKNOWN_EXPS = ["00000000-0000-0001-0001-999999999999"]
DRIFTS = ["00000000-0000-0000-0000-000000000001"]
UNKNWON_DRIFTS = ["00000000-0000-0000-0000-999999999999"]

# Constants for drift statuses
ALL_STATUS = ["Running", "Completed", "Failed"]

# User access and entitlements
CAN_READ = ["ai4eosc-read", "ai4eosc-edit", "ai4eosc-manage", "ai4eosc-admin", "ai4eosc-owner"]
CAN_EDIT = ["ai4eosc-edit", "ai4eosc-manage", "ai4eosc-admin", "ai4eosc-owner"]
CAN_MANAGE = ["ai4eosc-manage", "ai4eosc-admin", "ai4eosc-owner"]

# User negative access
NO_READ = ["ai4eosc-null"]
NO_EDIT = ["ai4eosc-null", "ai4eosc-read"]
NO_MANAGE = ["ai4eosc-null", "ai4eosc-read", "ai4eosc-edit"]

# Permissions for experiments
NEW_PERMISSIONS = [[{"level": "Read", "entity": "group"}]]
BAD_PERMISSIONS = [[{"entity": "g1", "level": "bad_level"}]]
