# Turso 505 Error - Troubleshooting Guide

## Error Summary

```
WSServerHandshakeError: 505, message='Invalid response status'
url='wss://car-listings-giorgamose.aws-eu-west-1.turso.io'
```

## Root Cause Analysis

The 505 error occurs during WebSocket connection handshake with Turso. This is **after** the SSL certificate issue, which means your network can reach Turso, but the server is rejecting the connection.

### Common Causes

1. **Invalid or Expired Credentials**
   - TURSO_AUTH_TOKEN might be expired
   - TURSO_DATABASE_URL might be incorrect
   - Credentials might not have permission to access this database

2. **Turso Service Issues**
   - Turso server might be temporarily down
   - There might be rate limiting applied to your account
   - The database might be in maintenance mode

3. **Network/Firewall Issues**
   - WebSocket connections might be blocked
   - ISP or corporate firewall might be blocking wss:// protocol
   - VPN might be interfering with the connection

## Solutions (in order of likelihood)

### Solution 1: Verify Credentials (MOST LIKELY)

1. Go to https://app.turso.tech
2. Log in to your account
3. Select your "car-listings" database
4. Check if the database is still active
5. Generate new credentials:
   - Click "Copy Connection String" or access the API tokens section
   - Update .env.local with new TURSO_DATABASE_URL and TURSO_AUTH_TOKEN
6. Test again

### Solution 2: Check Turso Service Status

1. Visit https://status.turso.tech
2. Check if there are any reported issues
3. If there are issues, wait for them to be resolved
4. Try again after 15 minutes

### Solution 3: Test with Different Network

1. Try running the script from a different network (mobile hotspot, different WiFi)
2. If it works on another network, your ISP/network might be blocking WebSocket connections
3. Solution: Use a VPN or contact your network administrator

### Solution 4: Check for Rate Limiting

If you recently:
- Made many connection attempts
- Ran many queries in a short time
- Have multiple processes connecting to the database

Then you might be rate-limited:

1. Wait 30 minutes before retrying
2. Check Turso dashboard for rate limit info
3. Upgrade your Turso plan if needed

### Solution 5: GitHub Actions Specific Issue

If this error appears in GitHub Actions but not locally:

1. The secrets might be configured incorrectly
2. Your IP might have changed (GitHub Actions servers rotate IPs)
3. Solutions:
   - Regenerate credentials in Turso
   - Update GitHub Secrets with new TURSO_DATABASE_URL and TURSO_AUTH_TOKEN
   - Go to Settings → Secrets and Variables → Actions

## Testing Steps

1. **Verify credentials are in .env.local:**
   ```
   TURSO_DATABASE_URL=libsql://car-listings-XXX.turso.io
   TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIs...
   ```

2. **Test database connection:**
   ```bash
   python test_db_connection.py
   ```

3. **Check database from Turso CLI:**
   ```bash
   turso db shell <your_database_url> --auth-token=<your_token>
   > SELECT 1;
   ```

4. **Try from different network:**
   - Use mobile hotspot or different WiFi
   - If it works, your network is blocking WebSocket

5. **Check GitHub Actions:**
   - View the action logs: Actions tab → select the failing action
   - Check if error is the same (505) or different
   - If different error, it's a configuration issue with secrets

## If All Else Fails

1. **Create new database:**
   - Go to https://app.turso.tech
   - Create a new database with different name
   - Get new credentials
   - Update .env.local
   - Migrate data if needed (export/import)

2. **Contact Turso Support:**
   - https://discord.gg/turso
   - https://github.com/tursodatabase/turso-client-py/issues

## Files Modified

- `database.py` - Added SSL certificate fix (aiohttp TCPConnector patching)
- `diagnose_turso.py` - Diagnostic tool to test connection
- `test_db_connection.py` - Simple test script

## Next Steps

1. Check and regenerate credentials (Solution 1)
2. Try from different network if possible
3. Check Turso service status
4. Run diagnostic tool: `python diagnose_turso.py`
5. Monitor Turso dashboard for usage/rate limits

