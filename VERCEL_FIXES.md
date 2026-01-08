# Vercel Deployment Fixes

## Problem
The deployed app at https://quarm-charm-calculator.vercel.app/ was returning "Forbidden" errors when uploading log files, with the JavaScript getting HTML instead of JSON.

## Root Cause
Vercel serverless functions have strict limits:
- **4.5MB request body limit** (we had 50MB)
- **10-60 second timeout** depending on plan
- Different error handling than traditional servers

## Solutions Implemented

### 1. Reduced File Size Limit
**File**: `app.py`
```python
# Changed from 50MB to 4MB (safe for Vercel)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
```

### 2. Client-Side File Size Validation
**File**: `templates/index.html`
- Added 4MB limit check before upload
- Provides user-friendly error message
- Prevents wasted upload attempts

### 3. Better Error Handling
**File**: `templates/index.html`
- Detects HTML responses (Vercel error pages)
- Handles "Forbidden", "Timeout", and other server errors
- Provides specific error messages for each case

### 4. Vercel Configuration
**File**: `vercel.json` (NEW)
```json
{
  "functions": {
    "app.py": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

### 5. Updated Documentation
**Files**: `README.md`, `VERCEL_DEPLOYMENT.md` (NEW), `CHANGELOG.md`
- Documented 4MB limit for Vercel
- Created comprehensive Vercel deployment guide
- Added troubleshooting section

### 6. Updated .gitignore
**File**: `.gitignore`
- Added `.vercel` directory

## No Code Changes Required

✅ **No shelling out** - Everything runs in Python
✅ **No disk writes** - All processing in memory using `io.BytesIO`
✅ **Pure Python library** - Log parser is imported directly
✅ **Stateless** - No persistent storage needed

## Testing

Verified locally:
```bash
✓ App imports successfully
✓ Max file size: 4.0MB
✓ Log parser loads spells from database
✓ 14 charm spells loaded dynamically
```

## Deployment Instructions

1. **Commit changes**:
```bash
git add .
git commit -m "Fix Vercel deployment - reduce file limit to 4MB"
git push origin main
```

2. **Vercel auto-deploys** from GitHub

3. **Verify deployment**:
   - Visit https://quarm-charm-calculator.vercel.app/
   - Test calculator (should work)
   - Test log upload with < 4MB file (should work)
   - Test log upload with > 4MB file (should show size error)

## User Communication

**For users with large log files:**

Instead of uploading a 10MB compressed log, they can:

1. Extract the ZIP
2. Open the .txt file
3. Copy only recent entries (e.g., last 1000 lines)
4. Save as a new file
5. Re-compress it
6. Upload (will be < 1MB)

**Example**:
```bash
# Extract recent log entries
tail -1000 eqlog_Fibbon_pq.proj.txt > eqlog_recent.txt

# Compress
zip eqlog_recent.zip eqlog_recent.txt

# Result: ~50KB instead of 10MB
```

## Future Improvements

If 4MB becomes too limiting:

1. **Upgrade Vercel Plan**: Pro plan has same 4.5MB limit
2. **Add S3 Upload**: For large files, upload to S3 first
3. **Streaming Processing**: Process log in chunks
4. **Client-Side Processing**: Parse logs in browser using JavaScript

For now, 4MB should handle 80-100MB of uncompressed logs, which is plenty for most use cases.

