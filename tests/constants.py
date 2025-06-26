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
CAN_READ = ["egi-read", "egi-edit", "egi-manage", "egi-admin", "egi-owner"]
CAN_EDIT = ["egi-edit", "egi-manage", "egi-admin", "egi-owner"]
CAN_MANAGE = ["egi-manage", "egi-admin", "egi-owner"]

# User negative access
NO_READ = ["egi-null"]
NO_EDIT = ["egi-null", "egi-read"]
NO_MANAGE = ["egi-null", "egi-read", "egi-edit"]

# Permissions for experiments
NEW_PERMISSIONS = [[{"level": "Read", "entity": "group"}]]
BAD_PERMISSIONS = [[{"entity": "g1", "level": "bad_level"}]]
