role_base = {"id": str, "name": str, "description": str}
role = {"id": str, "name": str, "description": str, "users": [{"name": str}]}

roles: list[role_base] = [role_base]
