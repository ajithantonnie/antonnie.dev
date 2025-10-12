# Chronos Timeline - Smart Caching System

## How the Enhanced Caching Works:

### 📊 **Cache Preservation Strategy:**
- **Keeps ALL previously fetched dates** - Never loses your historical data
- **Only updates when necessary** - Smart year-based refresh logic
- **Preserves cache across runs** - Builds up a comprehensive database over time

### 🔄 **Update Logic:**

1. **Same Year, Same Day**: Uses cached data (fast)
2. **Same Year, Next Day**: Uses cached data (fast)  
3. **Next Year, Same Date**: Updates with fresh data (smart refresh)
4. **More than 24 hours old**: Refreshes automatically

### 📈 **Example Timeline:**

```
Day 1 (Oct 12, 2025):
  - Fetch: 10-12, 12-25, 07-04
  - Cache: 3 dates from 2025

Day 30 (Nov 15, 2025):
  - Fetch: 11-15 (new date)
  - Cache: 4 dates from 2025
  - Uses cached data for any previously fetched dates

Day 365 (Oct 12, 2026):  
  - Fetch: 10-12 (updates 2025 data to 2026)
  - Cache: 4 dates (3 from 2025, 1 from 2026)
  - Preserves 12-25, 07-04, 11-15 from 2025
  - Only updates 10-12 because we requested it
```

### 💾 **Cache Statistics Tracking:**

Use `python history-automate.py --stats` to see:
- Total dates cached
- Dates by year  
- Cache age information
- Storage efficiency

### 🎯 **Benefits:**

✅ **Never lose data** - All previous dates preserved
✅ **Smart updates** - Only refreshes when needed (year change)
✅ **Fast loading** - Instant for cached dates
✅ **Efficient storage** - Only old entries (2+ years) are cleaned
✅ **Offline capability** - Works even if Wikipedia API is down

### 🚀 **Usage Examples:**

```bash
# Build up your cache over time
python history-automate.py --month 1 --day 1    # New Year
python history-automate.py --month 8 --day 15    # Independence Day  
python history-automate.py --month 12 --day 25  # Christmas
python history-automate.py                       # Today

# Check your cache
python history-automate.py --stats

# Next year, only requested dates get updated
# All other dates remain cached from previous year
```

This system ensures you build a comprehensive historical database while keeping data fresh when needed!