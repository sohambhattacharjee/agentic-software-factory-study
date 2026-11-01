PROFILES = {
    "baseline": {"repository_map": False, "persistent_memory": False, "verification": False, "review_pass": False},
    "context": {"repository_map": True, "persistent_memory": False, "verification": False, "review_pass": False},
    "memory": {"repository_map": True, "persistent_memory": True, "verification": False, "review_pass": False},
    "verification": {"repository_map": True, "persistent_memory": True, "verification": True, "review_pass": False},
    "review": {"repository_map": True, "persistent_memory": True, "verification": True, "review_pass": True},
}
