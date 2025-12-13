---
description: How to write code for this project
---

# Before Writing Any Code

1. **Read the code style guide**: `docs/CODE_STYLE.md`
2. **Read relevant module docs**: `docs/modules/*.md`

# Code Style Rules

- Write HUMAN code, not AI-generated code
- NO excessive comments (only comment the "why")
- NO verbose function names
- NO unnecessary wrapper functions
- NO over-engineering
- Keep files SHORT (< 150 lines)
- Use early returns, not nested ifs
- Prefer list comprehensions
- Only abstract after 3+ repetitions

# Bad vs Good Examples

```python
# BAD - AI code
def get_user_by_email_address(email_address: str) -> Optional[User]:
    """Get user by email address."""
    user = db.query(User).filter(User.email == email_address).first()
    return user

# GOOD - Human code  
def get_user(email):
    return db.query(User).filter_by(email=email).first()
```

# Testing

Before submitting code:
1. Does it pass lint/type checks?
2. Would a human write this?
3. Can you understand it in 5 seconds?
