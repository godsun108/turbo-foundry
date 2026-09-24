# Security

Do not commit secrets, credentials, access tokens, private keys, recovery phrases, personal identifiers, or sensitive customer/user data.

Use repository/environment secret stores for credentials. If a secret is accidentally committed, revoke/rotate it immediately; deleting the file from the latest commit is not sufficient.
