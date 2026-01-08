# Large File Upload Options for Vercel

## Current Limitation

Vercel serverless functions have a **4.5MB request body limit**. This is separate from:
- /tmp storage: 512MB (for processing)
- Function memory: 1024MB default
- Function timeout: 10-60 seconds depending on plan

## Option 1: Current Implementation (4MB)

**Pros:**
- ✅ No additional services needed
- ✅ No extra cost
- ✅ Simple implementation
- ✅ Handles 80-100MB uncompressed logs

**Cons:**
- ❌ Limited to 4MB compressed files
- ❌ Large logs need manual trimming

## Option 2: Vercel Blob Storage (50MB+)

### Architecture
```
Client → Vercel Blob → Processing Function → Response
```

### Implementation Steps

1. **Add Vercel Blob dependency**
```bash
npm install @vercel/blob
```

2. **Update requirements.txt**
```txt
Flask==3.0.0
Werkzeug==3.0.1
vercel-blob-python  # Or use REST API
```

3. **Two-phase upload process**

**Phase 1: Client uploads to Blob**
```javascript
// Get signed upload URL from backend
const response = await fetch('/api/get-upload-url');
const { url, token } = await response.json();

// Upload directly to Vercel Blob
const uploadResponse = await fetch(url, {
    method: 'PUT',
    body: file,
    headers: {
        'x-vercel-blob-token': token
    }
});

// Get blob URL
const { url: blobUrl } = await uploadResponse.json();
```

**Phase 2: Backend processes from Blob**
```python
from vercel_blob import download

@app.route('/api/analyze_log_from_blob', methods=['POST'])
def analyze_log_from_blob():
    blob_url = request.json['blob_url']
    
    # Download from Vercel Blob to /tmp
    blob_data = download(blob_url)
    
    # Process the file
    parser = CharmLogParser()
    stats = parser.parse_log_content(blob_data.decode('utf-8', errors='ignore'))
    
    return jsonify(stats)
```

**Pros:**
- ✅ Handles files up to 500MB
- ✅ Uses Vercel's infrastructure
- ✅ Automatic cleanup (TTL-based)
- ✅ Fast uploads (CDN-backed)

**Cons:**
- ❌ Requires Vercel Blob API (free tier: 1GB storage)
- ❌ More complex implementation
- ❌ Two-step upload process

### Cost
- **Free tier**: 1GB storage, 100GB bandwidth/month
- **Pro tier**: 100GB storage, 1TB bandwidth/month
- See: https://vercel.com/docs/storage/vercel-blob/usage-and-pricing

## Option 3: Client-Side Processing

### Architecture
```
Client Browser → Parse Log → Send Results → Server
```

### Implementation
Parse the log file entirely in JavaScript, extract charm events, and send only the statistics (a few KB) to the server.

**Pros:**
- ✅ No file size limits
- ✅ No server-side processing
- ✅ Works offline
- ✅ Instant results

**Cons:**
- ❌ Requires JavaScript implementation
- ❌ Client needs to unzip locally
- ❌ Browser compatibility concerns
- ❌ No server-side validation

## Option 4: AWS S3 Direct Upload

### Architecture
```
Client → S3 (signed URL) → Lambda/Vercel Function → Response
```

Similar to Vercel Blob but using AWS S3.

**Pros:**
- ✅ Handles very large files (5GB+)
- ✅ More control over storage
- ✅ Lower cost at scale

**Cons:**
- ❌ Requires AWS account
- ❌ More complex setup
- ❌ Additional service to manage

## Recommendation

### For Now: Keep 4MB Limit
The vast majority of users will compress their logs to < 4MB. Users with larger files can:
- Compress only recent log entries
- Use the command-line tool locally

### For Future: Implement Vercel Blob
If users frequently hit the 4MB limit, implement Vercel Blob:
1. Adds ~1-2 hours of development time
2. Supports up to 500MB files
3. Uses Vercel's native infrastructure
4. Free tier is generous (1GB storage)

### Implementation Priority
1. ✅ **Ship 4MB limit now** - Works for 95% of users
2. 📊 **Monitor usage** - Track how many users hit the limit
3. 🚀 **Add Vercel Blob** - Only if needed based on usage data

## Example: Tail Recent Log Entries

For users with large logs:

```bash
# Linux/Mac: Get last 5000 lines (usually covers several hours)
tail -5000 eqlog_Fibbon_pq.proj.txt > eqlog_recent.txt
zip eqlog_recent.zip eqlog_recent.txt

# Windows PowerShell
Get-Content eqlog_Fibbon_pq.proj.txt -Tail 5000 | Out-File eqlog_recent.txt
Compress-Archive -Path eqlog_recent.txt -DestinationPath eqlog_recent.zip
```

5000 lines of log text:
- Uncompressed: ~500KB
- Compressed: ~25KB
- Covers: 4-6 hours of gameplay
- Contains: 50-200 charm events

This easily fits under 4MB and provides plenty of data for analysis.

