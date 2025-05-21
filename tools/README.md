# Tools

## 🔐 JWT Token Generator (for Local Dev)

This command-line tool generates JSON Web Tokens (JWTs) for local testing of authenticated API routes in the Zap project. It uses the same signing secret as the backend (`/Zap/AUTH_SECRET` in AWS SSM) and supports role-based token generation.

## Options

| Flag       | Description                                                                       | Default  |
| ---------- | --------------------------------------------------------------------------------- | -------- |
| `--expiry` | Expiration time in hours                                                          | `1`      |
| `--roles`  | Space-separated list of allowed roles: `admin`, `member`, `eboard`, `recruitment` | `member` |


## 🚀 Usage

```bash
python tools/generate_jwt_token.py [--expiry HOURS] [--roles ROLE [ROLE ...]]
```
## ✅ Examples
Generate a token for a single role:

```bash
python tools/generate_jwt_token.py --roles admin
```

Generate a token with multiple roles and longer expiry:

```bash
python tools/generate_jwt_token.py --expiry 6 --roles admin member recruitment
```