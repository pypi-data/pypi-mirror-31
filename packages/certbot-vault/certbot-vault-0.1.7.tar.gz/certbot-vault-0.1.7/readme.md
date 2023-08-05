
# Certbot-Vault
Certbot plugin for Vault

Installation guide:
* Install [Vault](https://www.vaultproject.io/)
* Get a Vault token
* Deploy latest version of [Certbot](https://github.com/certbot/certbot)
* Install certbot-vault `plugin pip install certbot-vault`

## Use cases:
* Get/Renew and store new certificate in vault


 ``` certbot certonly -i certbot-vault:vault --certbot-vault:vault-vault-token=your_vault_token certbot-vault:http://your-vault.server:port```
