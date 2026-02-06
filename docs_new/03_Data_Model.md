# 🗃️ AskTennis AI - Data Model Architecture

## Overview

The AskTennis AI system is built on a comprehensive database containing 147 years of tennis history (1877-2024). The data model supports **DuckDB** (local development, high-performance analytics), **SQLite** (local fallback), and **Cloud SQL PostgreSQL** (production) databases, designed to support complex tennis analytics, player comparisons, and historical analysis. Additionally, a separate authentication database stores user credentials and session information.

## 📊 Database Schema Diagram

### **Visual Database Schema**
```
┌─────────────────────────────────────────────────────────────────┐
│                        MATCHES TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner_id  │  loser_id   │  surface  │  score  │
│  tourney_name │  winner_name │  loser_name │  round    │  minutes │
│  event_year  │  event_month │  event_date │  w_ace    │  l_ace   │
│  w_df        │  l_df       │  w_svpt     │  l_svpt    │  w_1stIn │
│  l_1stIn     │  w_1stWon   │  l_1stWon   │  w_2ndWon  │  l_2ndWon│
│  w_bpSaved   │  l_bpSaved  │  w_bpFaced  │  l_bpFaced │  ...    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PLAYERS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  player_id  │  name_first  │  name_last  │  hand     │  height  │
│  dob        │  ioc         │  wikidata_id │  tour      │  full_name │
│  country    │  birth_year  │  birth_month│  birth_date│  ...    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RANKINGS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  ranking_date │  rank  │  player  │  points  │  tournaments  │
│  player_id    │  tour  │  ...     │          │               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOUBLES_MATCHES TABLE                      │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner1_id │  winner2_id │  loser1_id │  loser2_id │
│  winner1_name │  winner2_name │  loser1_name │  loser2_name │  score │
│  ...         │             │             │             │            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION DATABASE                     │
├─────────────────────────────────────────────────────────────────┤
│  USERS TABLE                                                   │
│  id          │  username    │  hashed_password │  created_at   │
│  last_login  │  ...        │                  │               │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Core Tables

### 1. **MATCHES Table** (Primary Data)
- **Purpose**: Stores all singles tennis matches
- **Records**: 1,693,626+ matches (1877-2024)
- **Key Features**:
  - Complete match statistics (aces, double faults, service points)
  - Player metadata (handedness, nationality, height, age)
  - Tournament information (surface, level, date)
  - Ranking context (winner/loser rankings)
  - Detailed service statistics (1st serve %, break points)
- **Indexes**: 
  - `winner_id`, `loser_id`, `event_year`, `tourney_name`, `surface`
  - Composite: `(event_year, surface)`, `(tourney_name, event_year)`

### 2. **PLAYERS Table** (Player Metadata)
- **Purpose**: Stores player information and metadata
- **Records**: 136,025+ players
- **Key Features**:
  - Physical attributes (height, handedness)
  - Personal information (birth date, nationality)
  - Career information (tour, full name)
  - External references (Wikidata ID)
- **Indexes**: 
  - `player_id`, `full_name`, `ioc` (country code)
  - Full-text search on `name_first`, `name_last`

### 3. **RANKINGS Table** (Historical Rankings)
- **Purpose**: Stores historical ranking data
- **Records**: 5,335,249+ ranking records (1973-2024)
- **Key Features**:
  - Weekly ranking updates
  - Ranking points and tournament counts
  - Tour-specific rankings (ATP, WTA)
  - Historical ranking trajectories
- **Indexes**: 
  - `player`, `ranking_date`, `tour`
  - Composite: `(player, ranking_date)`

### 4. **DOUBLES_MATCHES Table** (Doubles Data)
- **Purpose**: Stores doubles tennis matches
- **Records**: 26,399+ matches (2000-2020)
- **Key Features**:
  - Team-based match data
  - Individual player statistics
  - Tournament and surface information

### 5. **USERS Table** (Authentication Database)
- **Purpose**: Stores user authentication information
- **Database**: Separate database (SQLite or Cloud SQL)
- **Key Features**:
  - Username (unique)
  - Bcrypt-hashed password
  - Account creation timestamp
  - Last login timestamp
- **Security**: 
  - Passwords never stored in plain text
  - HttpOnly cookies for session management

## 📈 Database Views

### 1. **matches_with_full_info**
Detailed view combining match data with full player names, handedness, and country codes for both winner and loser. Optimized for common query patterns.

### 2. **matches_with_rankings**
Detailed view linking match results with the exact ranking of players at the date of the match. Enables ranking-based analysis.

### 3. **player_rankings_history**
Optimized view for retrieving a player's complete ranking history for chart generation. Pre-aggregated for performance.

## 🔍 Database Indexes

### 1. **Performance Indexes**

**Match-based Indexes:**
- `matches(winner_id)` - Fast winner lookups
- `matches(loser_id)` - Fast loser lookups
- `matches(event_year)` - Year-based filtering
- `matches(tourney_name)` - Tournament filtering
- `matches(surface)` - Surface-based analysis
- `matches(event_year, surface)` - Composite for common queries

**Player-based Indexes:**
- `players(player_id)` - Primary key
- `players(full_name)` - Name lookups
- `players(ioc)` - Country-based queries

**Ranking-based Indexes:**
- `rankings(player)` - Player ranking history
- `rankings(ranking_date)` - Date-based queries
- `rankings(player, ranking_date)` - Composite for time-series

### 2. **Full-Text Search**
- Player names support case-insensitive matching
- Tournament names support partial matching
- Uses database-specific full-text capabilities (PostgreSQL FTS, DuckDB text search)

## 🎯 Data Model Design Principles

### 1. **Normalization**
- **3NF Compliance**: Third Normal Form database design to reduce redundancy.
- **Referential Integrity**: Foreign key constraints linking matches to players (where supported).
- **Data Consistency**: Constraints ensure data quality.

### 2. **Performance Optimization**
- **Strategic Indexing**: Indexes on frequently queried columns and composite indexes for common query patterns.
- **Caching Strategy**: 
  - Backend utilizes Redis/DiskCache for query results.
  - LRU caching for static lookups (Player names, Tournament lists).
- **Case-Insensitive Matching**: Queries use `LOWER()` logic or database-specific collation (NOCASE for SQLite).
- **Query Optimization**: Database-specific optimizations (DuckDB analytics, PostgreSQL query planner).

### 3. **Scalability**
- **Cloud SQL Support**: Fully compatible with PostgreSQL for production workloads.
- **Optimized Views**: Pre-computed joins for heavy analytical queries.
- **Connection Pooling**: Efficient connection management for high concurrency.
- **Partitioning Ready**: Schema supports future partitioning strategies.

### 4. **Multi-Database Support**
- **DuckDB**: Optimized for analytical queries, columnar storage.
- **SQLite**: Simple file-based storage for development.
- **Cloud SQL PostgreSQL**: Production-grade relational database with advanced features.

## 🔧 Database Configuration

### 1. **DuckDB (Local Development - Recommended)**
- **File**: `tennis_data_with_mcp.db`
- **Characteristics**:
  - High-performance analytical database
  - Columnar storage optimized for analytics
  - Fast aggregations and joins
  - Zero-config, single-file deployment
- **Use Case**: Local development, data analysis, testing

### 2. **SQLite (Local Fallback)**
- **File**: `tennis_data.db` or configured path
- **Characteristics**:
  - Simple file-based database
  - Zero-configuration
  - Good for single-user scenarios
  - Portable and easy to backup
- **Use Case**: Simple local development, fallback option

### 3. **Cloud SQL PostgreSQL (Production)**
- **Configuration**: Via environment variables
- **Characteristics**:
  - Managed PostgreSQL database
  - Scalable and production-ready
  - Supports multiple concurrent users
  - Automatic backups and high availability
  - Advanced features (full-text search, JSON support)
- **Use Case**: Production deployments, multi-user scenarios

### 4. **Authentication Database**
- **SQLite**: `auth.db` (local development)
- **Cloud SQL**: `asktennis_auth` database (production)
- **Purpose**: Separate database for user authentication
- **Security**: Isolated from main data, encrypted passwords

## 🔄 Database Factory Pattern

The system uses a **Database Factory** pattern to automatically detect and configure the appropriate database:

```python
# Automatic detection from environment
db_config = DatabaseFactory.create_config()

# Explicit configuration
db_config = DatabaseFactory.create_config(
    db_type="duckdb",
    db_path="duckdb:///data/tennis_data.db"
)
```

**Detection Logic:**
1. Check `DB_TYPE` environment variable
2. Check for Cloud SQL configuration (`INSTANCE_CONNECTION_NAME`)
3. Default to DuckDB if available, otherwise SQLite

## 📊 Data Types & Constraints

### **Match Data Types**
- **Dates**: Stored as DATE or INTEGER (year, month, day)
- **Scores**: VARCHAR for flexible score formats
- **Statistics**: INTEGER or FLOAT for numeric values
- **Names**: VARCHAR with appropriate length limits

### **Constraints**
- **Primary Keys**: All tables have primary key constraints
- **Foreign Keys**: Referential integrity where supported
- **Unique Constraints**: Usernames, player IDs
- **Check Constraints**: Valid date ranges, positive values

## 🔍 Query Optimization Strategies

### 1. **Schema Pruning**
- Identifies relevant tables/columns based on query keywords
- Reduces schema information in LLM prompts by 80%
- Faster LLM inference and lower token costs

### 2. **Index Usage**
- Query planner automatically uses appropriate indexes
- Composite indexes for multi-column queries
- Covering indexes for common SELECT patterns

### 3. **Query Patterns**
- Prefer indexed columns in WHERE clauses
- Use JOINs efficiently with indexed foreign keys
- Limit result sets to prevent large payloads (default: 100 rows)

## 🛡️ Data Security

### 1. **Access Control**
- Database user authentication
- Role-based access control (production)
- Read-only access for application users

### 2. **Data Protection**
- Encrypted connections (Cloud SQL)
- Encrypted data at rest (Cloud SQL)
- Secure credential storage (Secret Manager)

### 3. **Backup & Recovery**
- Automatic backups (Cloud SQL)
- Point-in-time recovery
- Export capabilities for data migration

## 📈 Data Volume & Performance

### **Current Data Volumes**
- **Matches**: 1.7M+ records
- **Players**: 136K+ records
- **Rankings**: 5.3M+ records
- **Doubles**: 26K+ records

### **Performance Metrics**
- **Query Latency**: < 100ms for indexed queries
- **Cache Hit Rate**: 60-80% for repeated queries
- **Concurrent Users**: Supports 100+ concurrent connections (Cloud SQL)

## 🔮 Future Enhancements

### 1. **Advanced Features**
- **Materialized Views**: For complex aggregations
- **Partitioning**: For large tables by year
- **Full-Text Search**: Enhanced player/tournament search
- **JSON Columns**: For flexible metadata storage

### 2. **Analytics Optimization**
- **Columnar Storage**: DuckDB's columnar format for analytics
- **Time-Series Optimization**: For ranking data
- **Aggregation Tables**: Pre-computed statistics

### 3. **Data Expansion**
- **Real-time Updates**: Live match data integration
- **Historical Expansion**: Additional historical data sources
- **Player Profiles**: Enhanced player metadata

---

## 🎯 Key Data Model Benefits

1. **Flexibility**: Support for multiple database backends
2. **Performance**: Optimized indexes and query patterns
3. **Scalability**: Ready for production workloads
4. **Security**: Separate authentication database
5. **Maintainability**: Clean schema with proper normalization
6. **Extensibility**: Easy to add new tables and columns
7. **Analytics-Ready**: Optimized for analytical queries

This data model provides a solid foundation for comprehensive tennis analytics while maintaining flexibility, performance, and scalability across different deployment scenarios.
