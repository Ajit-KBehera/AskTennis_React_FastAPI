# 🗃️ AskTennis AI - Data Model Architecture

## Overview

The AskTennis AI system is built on a comprehensive database containing 147 years of tennis history (1877-2024). The data model supports both SQLite (local development) and Cloud SQL/PostgreSQL (production) databases, designed to support complex tennis analytics, player comparisons, and historical analysis.

## 📊 Database Schema Diagram

### **Visual Database Schema**
```
┌─────────────────────────────────────────────────────────────────┐
│                        MATCHES TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner_id  │  loser_id   │  surface  │  score  │
│  tourney_name │  winner_name │  loser_name │  round    │  minutes │
│  event_year  │  event_month │  event_date │  w_ace    │  l_ace   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PLAYERS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  player_id  │  name_first  │  name_last  │  hand     │  height  │
│  dob        │  ioc         │  wikidata_id │  tour      │  full_name │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RANKINGS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  ranking_date │  rank  │  player  │  points  │  tournaments  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOUBLES_MATCHES TABLE                      │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner1_id │  winner2_id │  loser1_id │  loser2_id │
│  winner1_name │  winner2_name │  loser1_name │  loser2_name │  score │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Core Tables

### 1. **MATCHES Table** (Primary Data)
- **Purpose**: Stores all singles tennis matches
- **Records**: 1,693,626 matches (1877-2024)
- **Key Features**:
  - Complete match statistics (aces, double faults, service points)
  - Player metadata (handedness, nationality, height, age)
  - Tournament information (surface, level, date)
  - Ranking context (winner/loser rankings)

### 2. **PLAYERS Table** (Player Metadata)
- **Purpose**: Stores player information and metadata
- **Records**: 136,025 players
- **Key Features**:
  - Physical attributes (height, handedness)
  - Personal information (birth date, nationality)
  - Career information (tour, full name)
  - External references (Wikidata ID)

### 3. **RANKINGS Table** (Historical Rankings)
- **Purpose**: Stores historical ranking data
- **Records**: 5,335,249 ranking records (1973-2024)
- **Key Features**:
  - Weekly ranking updates
  - Ranking points and tournament counts
  - Tour-specific rankings (ATP, WTA)
  - Historical ranking trajectories

### 4. **DOUBLES_MATCHES Table** (Doubles Data)
- **Purpose**: Stores doubles tennis matches
- **Records**: 26,399 matches (2000-2020)
- **Key Features**:
  - Team-based match data
  - Individual player statistics

## 📈 Database Views

### 1. **matches_with_full_info**
Detailed view combining match data with full player names, handedness, and country codes for both winner and loser.

### 2. **matches_with_rankings**
Detailed view linking match results with the exact ranking of players at the date of the match.

### 3. **player_rankings_history**
Optimized view for retrieving a player's complete ranking history for chart generation.

## 🔍 Database Indexes

### 1. **Performance Indexes**
- **Match-based**: `winner_id`, `loser_id`, `event_year`, `tourney_name`, `surface`.
- **Player-based**: `player_id`, `full_name`, `ioc`.
- **Ranking-based**: `player`, `ranking_date`.

### 2. **Composite Indexes**
- `matches(event_year, surface)`
- `rankings(player, ranking_date)`

## 🎯 Data Model Design Principles

### 1. **Normalization**
- **3NF Compliance**: Third Normal Form database design.
- **Referential Integrity**: Foreign key constraints linking matches to players.

### 2. **Performance Optimization**
- **Strategic Indexing**: Indexes on frequently queried columns.
- **Caching Strategy**: Backend utilizes LRU caching for static lookups (Player names, Tournament lists).
- **Case-Insensitive Matching**: Queries use `LOWER()` logic or `NOCASE` collation.

### 3. **Scalability**
- **Cloud SQL Support**: Fully compatible with PostgreSQL for production workloads.
- **Optimized Views**: Pre-computed joins for heavy analytical queries.

## 🔧 Database Configuration

### 1. **SQLite (Local)**
- File: `tennis_data.db`
- Zero-config, single-file deployment.

### 2. **Cloud SQL (Production)**
- Configured via Environment Variables.
- Supports high-concurrency access for the FastAPI backend.
