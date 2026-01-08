# Vercel Deployment Guide

This guide covers deploying the Quarm Charm Calculator to [Vercel](https://vercel.com).

## Prerequisites

- A Vercel account (free tier works)
- Git repository with your code

## Deployment Steps

### 1. Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/QuarmCharmCalculator)

Or manually:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project directory
cd QuarmCharmCalculator
vercel
```

### 2. Configuration

The project includes a `vercel.json` file with optimized settings:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "functions": {
    "app.py": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

## Vercel-Specific Limitations

### File Upload Limits

Vercel serverless functions have a **4.5MB request body limit**. We've set the app limit to **4MB** to be safe.

- **Local/Docker deployments**: Can handle 50MB files
- **Vercel deployment**: Limited to 4MB compressed ZIP files
- **Solution**: For large logs, compress only recent log entries

### Function Timeout

- **Hobby plan**: 10 seconds
- **Pro plan**: 60 seconds
- **Our setting**: 30 seconds (adjust in `vercel.json` if needed)

### Memory

- **Default**: 1024MB (1GB)
- **Maximum**: 3008MB on Pro plan
- Our calculator typically uses < 200MB

## Environment Variables

No environment variables are required for basic operation.

## Custom Domain

To use a custom domain:

1. Go to your Vercel project settings
2. Navigate to "Domains"
3. Add your domain and follow DNS instructions

## Monitoring

Vercel provides:
- Real-time logs in the dashboard
- Analytics on the "Analytics" tab
- Error tracking in "Logs"

## Troubleshooting

### "Forbidden" Error on Log Upload

**Symptoms**: Upload fails with "Forbidden" error or "Unexpected token 'F'"

**Causes**:
- File exceeds 4MB limit
- Request timeout
- Vercel platform issue

**Solutions**:
1. Check file size - must be < 4MB
2. Try compressing a smaller portion of your log file
3. Check Vercel status page for platform issues

### Function Timeout

**Symptoms**: Request hangs then fails after 10-30 seconds

**Solutions**:
1. Reduce the number of simulations in calculator
2. Upload smaller log files
3. Upgrade to Vercel Pro for 60s timeout

### Build Failures

**Symptoms**: Deployment fails during build

**Solutions**:
1. Ensure `requirements.txt` only includes runtime dependencies
2. Check that `charm_spells_data.py` exists (run `make refresh-spells` locally first)
3. Verify all imports are available

## Local Testing Before Deploy

Test the production configuration locally:

```bash
# Set production environment
export FLASK_ENV=production

# Run with production settings
python app.py
```

## Updating the Deployment

### Via Git

```bash
git add .
git commit -m "Update calculator"
git push origin main
```

Vercel auto-deploys on push to main branch.

### Via Vercel CLI

```bash
vercel --prod
```

## Performance Optimization

### For Vercel Deployment

1. **Minimize dependencies**: Keep `requirements.txt` lean
2. **Cache static assets**: Vercel automatically caches static files
3. **Optimize simulations**: Default to fewer simulations (5000-10000)
4. **Precompute spell data**: Use `make refresh-spells` before deploying

## Security Considerations

1. **No sensitive data**: App doesn't store user data
2. **File validation**: ZIP files are validated before processing
3. **Size limits**: Enforced both client-side and server-side
4. **No disk writes**: All processing in memory (Vercel-safe)

## Cost Estimates

### Hobby Plan (Free)
- ✅ Perfect for this app
- 100GB bandwidth/month
- 100 hours serverless execution
- 10s function timeout

### Pro Plan ($20/month)
- 1TB bandwidth
- 1000 hours execution
- 60s function timeout
- Custom domains included

## Support

For Vercel-specific issues:
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Status](https://www.vercel-status.com/)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

For calculator issues:
- Check the main README.md
- Open an issue on GitHub

