# ACLED OAuth Setup

## Quick Setup

The Risk API now uses OAuth2 authentication for ACLED. Set your credentials as environment variables:

```bash
export ACLED_USERNAME=kdandu3@charlotte.edu
export ACLED_PASSWORD=Theater6#
export ACLED_CLIENT_ID=acled
```

## How It Works

1. **OAuth Token Request**: The Risk API automatically requests an OAuth token using your credentials
2. **Token Caching**: The token is cached in memory until it expires
3. **Auto-Refresh**: When the token expires, it's automatically refreshed
4. **Bearer Token**: All ACLED API requests use the Bearer token in the Authorization header

## Local Testing

```bash
# Set environment variables
export ACLED_USERNAME=kdandu3@charlotte.edu
export ACLED_PASSWORD=Theater6#
export ACLED_CLIENT_ID=acled

# Run Risk API locally
cd risk-api
python app.py

# Test ACLED endpoint
curl http://localhost:8081/risk/Taiwan
```

## Cloud Run Deployment

### Option 1: Set via Environment Variables

```bash
gcloud run services update risk-api \
  --set-env-vars "ACLED_USERNAME=kdandu3@charlotte.edu,ACLED_PASSWORD=Theater6#,ACLED_CLIENT_ID=acled" \
  --region us-central1
```

### Option 2: Use Secret Manager (Recommended for Production)

```bash
# Create secrets
echo -n "kdandu3@charlotte.edu" | gcloud secrets create acled-username --data-file=-
echo -n "Theater6#" | gcloud secrets create acled-password --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding acled-username \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding acled-password \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run service to use secrets
gcloud run services update risk-api \
  --update-secrets ACLED_USERNAME=acled-username:latest,ACLED_PASSWORD=acled-password:latest \
  --region us-central1
```

## Test OAuth Token

You can test the OAuth token directly:

```bash
curl -X POST "https://acleddata.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=kdandu3@charlotte.edu" \
  -d "password=Theater6#" \
  -d "grant_type=password" \
  -d "client_id=acled"
```

This should return:
```json
{
  "access_token": "your_token_here",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Verify Risk API is Working

```bash
# Check health
curl https://risk-api-xxxxx.run.app/

# Get risk data (should use OAuth token automatically)
curl https://risk-api-xxxxx.run.app/risk/Taiwan

# Get detailed risk breakdown
curl https://risk-api-xxxxx.run.app/risk/details
```

## Troubleshooting

### Token Not Working
- Verify credentials are correct
- Check token hasn't expired (tokens expire after 1 hour)
- Review logs: `gcloud run services logs read risk-api --region us-central1`

### 401 Unauthorized
- Token may have expired - the API should auto-refresh
- Check credentials are set correctly
- Verify ACLED account is active

### Rate Limits
- ACLED API may have rate limits
- Token caching helps reduce authentication requests
- Monitor API usage

## Security Notes

⚠️ **Never commit passwords to git!**

- Use environment variables for local development
- Use Google Cloud Secret Manager for production
- Rotate passwords regularly
- Monitor access logs

## Next Steps

1. ✅ Set environment variables
2. ✅ Test locally
3. ✅ Deploy to Cloud Run
4. ✅ Verify OAuth token is working
5. ✅ Test risk API endpoints
6. ✅ Monitor logs for any issues

