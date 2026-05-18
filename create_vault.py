# create_vault.py — run once, save the output
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

vault = client.beta.vaults.create(name="Notion Credentials")

credential = client.beta.vaults.credentials.create(
    vault.id,
    display_name="Notion (my workspace)",
    auth={
        "type": "mcp_oauth",
        "mcp_server_url": "https://mcp.notion.com/mcp",
        "access_token": "YOUR_ACCESS_TOKEN",
        "expires_at": "2026-06-01T00:00:00Z",
        "refresh": {
            "refresh_token": "YOUR_REFRESH_TOKEN",
            "client_id": "YOUR_CLIENT_ID",
            "token_endpoint": "https://api.notion.com/v1/oauth/token",
            "token_endpoint_auth": {
                "type": "client_secret_basic",
                "client_secret": "YOUR_CLIENT_SECRET"
            }
        }
    }
)

print(f"VAULT_ID={vault.id}")
print(f"CREDENTIAL_ID={credential.id}")
# Save VAULT_ID to your .env file