# envault

> Lightweight utility to encrypt and manage per-project `.env` files with key rotation support.

---

## Installation

```bash
pip install envault
```

---

## Usage

**Encrypt your `.env` file:**

```bash
envault encrypt .env --output .env.vault
```

**Decrypt when needed:**

```bash
envault decrypt .env.vault --output .env
```

**Rotate encryption keys:**

```bash
envault rotate .env.vault --new-key $(envault keygen)
```

**Use in Python:**

```python
from envault import load_vault

load_vault(".env.vault", key="your-secret-key")

import os
print(os.getenv("DATABASE_URL"))
```

The vault file (`.env.vault`) is safe to commit to version control. Store your key in a secrets manager or CI/CD environment variable — never in the repository.

---

## Workflow

1. Add `.env` to `.gitignore`
2. Encrypt with `envault encrypt .env`
3. Commit `.env.vault`
4. Share the key securely with teammates
5. Rotate keys as needed with `envault rotate`

---

## License

MIT © [envault contributors](https://github.com/your-org/envault)