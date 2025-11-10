# Database Alternatives to Turso

## Quick Comparison Table

| Database | Setup | Ease | Reliability | Free Tier | Python Support | Recommendation |
|----------|-------|------|-------------|-----------|-----------------|-----------------|
| **Supabase** | ⭐⭐⭐⭐⭐ | Very Easy | Excellent | 500MB | Excellent | **🥇 BEST** |
| **Neon** | ⭐⭐⭐⭐⭐ | Very Easy | Excellent | 0.5GB | Excellent | **🥈 GREAT** |
| **MongoDB Atlas** | ⭐⭐⭐⭐ | Easy | Excellent | 512MB | Excellent | **🥉 GOOD** |
| **Firebase** | ⭐⭐⭐⭐ | Medium | Excellent | Good | Fair | Good |
| **SQLite Local** | ⭐⭐⭐ | Very Easy | Good | Unlimited | Excellent | For testing |
| **Railway** | ⭐⭐⭐⭐ | Easy | Excellent | $5/mo | Excellent | Good alternative |
| **Render** | ⭐⭐⭐⭐ | Easy | Excellent | Limited | Excellent | Good alternative |

---

## Top 3 Recommendations

### 1. 🥇 **Supabase** (PostgreSQL-based)

**Why it's best for you:**
- PostgreSQL (rock-solid, proven)
- Easiest migration from SQL
- 500MB free tier (more than enough for car listings)
- Excellent Python support
- Works great with GitHub Actions
- No SELECT query issues (battle-tested)

**Setup:**
```bash
# 1. Go to https://supabase.com
# 2. Create free account
# 3. Create new project
# 4. Get connection string
# 5. Install PostgreSQL driver:
pip install psycopg2-binary

# 6. Update .env.local:
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**Code example:**
```python
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT * FROM seen_listings")
results = cursor.fetchall()
```

**Pros:**
- ✅ PostgreSQL reliability
- ✅ 500MB free (sufficient)
- ✅ Excellent Python support
- ✅ No SELECT issues (proven)
- ✅ Auto-backup features
- ✅ Easy migration from Turso

**Cons:**
- ⚠️ Requires connection pooling for serverless

---

### 2. 🥈 **Neon** (PostgreSQL-based)

**Why consider it:**
- Serverless PostgreSQL (optimized for functions)
- 0.5GB free storage
- Built for GitHub Actions/CI-CD
- Same reliability as Supabase

**Setup:**
```bash
# 1. Go to https://neon.tech
# 2. Sign up with GitHub (quickest)
# 3. Get connection string
# 4. Same code as Supabase
```

**Pros:**
- ✅ Serverless-first design
- ✅ Optimized for GitHub Actions
- ✅ PostgreSQL reliability
- ✅ Better for intermittent usage

**Cons:**
- ⚠️ Cold starts (minor, ~1-2 seconds)
- ⚠️ Slightly less free tier than Supabase

---

### 3. 🥉 **MongoDB Atlas** (Document-based)

**Why consider it:**
- No schema needed (flexible)
- 512MB free tier
- Different model might avoid SELECT issues
- Great for unstructured data

**Setup:**
```bash
# 1. Go to https://www.mongodb.com/cloud/atlas
# 2. Create free account
# 3. Create cluster
# 4. Install driver:
pip install pymongo

# 5. Update .env.local:
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

**Code example:**
```python
from pymongo import MongoClient

client = MongoClient(os.getenv('MONGODB_URL'))
db = client['car_listings']
collection = db['listings']

# Insert
collection.insert_one({'id': '123', 'make': 'Toyota'})

# Find
result = collection.find_one({'id': '123'})
```

**Pros:**
- ✅ No schema migration
- ✅ Flexible data structure
- ✅ NoSQL (different approach)
- ✅ Great free tier

**Cons:**
- ⚠️ Different API (requires code changes)
- ⚠️ Less suitable for relational queries

---

## Other Solid Options

### **Railway** (PostgreSQL/MySQL)
- https://railway.app
- $5/month credit (free tier)
- Very easy setup
- Great for side projects

### **Render** (PostgreSQL/MySQL)
- https://render.com
- Limited free tier but solid
- Easy to use
- Good support

---

## Migration Strategy

If you choose **Supabase** or **Neon** (recommended), migration is straightforward:

### Step 1: Export from Turso
```bash
# Using Python
import sqlite3
conn = sqlite3.connect(':memory:')
# or export SQL dump from Turso dashboard
```

### Step 2: Create Tables in New DB
```sql
CREATE TABLE seen_listings (
    id TEXT PRIMARY KEY,
    created_at TEXT,
    last_notified_at TEXT,
    notified INTEGER
);

CREATE TABLE vehicle_details (
    listing_id TEXT PRIMARY KEY,
    make TEXT,
    model TEXT,
    year INTEGER,
    price REAL,
    currency TEXT,
    mileage_km INTEGER,
    location TEXT,
    seller_name TEXT,
    -- ... other fields
);
```

### Step 3: Update database.py
Replace Turso with PostgreSQL:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            return self.cursor.fetchall()
        self.conn.commit()
        return True
```

---

## Quick Decision Matrix

Choose **Supabase** if you:
- Want simplest migration from Turso
- Need reliable PostgreSQL
- Want best free tier
- Don't mind extra features

Choose **Neon** if you:
- Want serverless optimization
- Run infrequently (GitHub Actions)
- Want zero management
- Prefer smaller footprint

Choose **MongoDB Atlas** if you:
- Want schema-free design
- Don't want to migrate SQL
- Prefer document storage
- Like flexible data models

---

## Immediate Action Plan

### Option A: Switch to Supabase (RECOMMENDED)
1. Create Supabase account: https://supabase.com
2. Create new project (takes 2 minutes)
3. Copy PostgreSQL connection string
4. Create new database.py with psycopg2
5. Copy data from Turso (or start fresh)
6. Update .env.local
7. Test with `python test_db_connection.py`

### Option B: Stay with Turso but Debug Further
1. Wait 30 minutes (database initialization)
2. Contact Turso support with clear error details
3. Ask for database diagnostic

### Option C: Use SQLite Locally (Temporary)
Good for testing before full migration:
```python
import sqlite3
conn = sqlite3.connect('car_listings.db')
cursor = conn.cursor()
# Full SQL compatibility, no remote issues
```

---

## My Recommendation

**Switch to Supabase** because:
1. ✅ No more 505 errors (PostgreSQL is proven)
2. ✅ Better free tier than Turso
3. ✅ More reliable for production
4. ✅ Easy migration from SQL
5. ✅ Better community support
6. ✅ Works perfectly with GitHub Actions

**Time to migrate:** ~30 minutes
**Risk level:** Very low (no code changes needed for database operations)

---

## Files to Update

Once you choose new database:
1. `database.py` - Change database driver
2. `.env.local` - Update connection string
3. `requirements.txt` - Update dependencies
4. Run migrations/data import

The core application logic in `main.py` needs **zero changes** if you use SQL-based database!

