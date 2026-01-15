# 👤 AskTennis AI - Use Case Diagram

## Overview

This document outlines the primary actors and use cases for the AskTennis AI system, highlighting the interactions between users and the React+FastAPI platform.

## 🎭 Actors

### 1. **Tennis Analyst / Researcher**
-   **Goal**: Deep dive into historical data.
-   **Behavior**: Uses complex filters, looks at raw data tables, exports results.

### 2. **Casual Fan**
-   **Goal**: Quick answers to trivia.
-   **Behavior**: Uses natural language chat ("Who is the best player on grass?").

### 3. **System Administrator**
-   **Goal**: Maintain system health.
-   **Behavior**: Monitors API logs, manages database updates.

## 📋 Use Cases

### **Core Platform Functionality**

#### **UC-01: Natural Language Query**
-   **Actor**: Casual Fan, Analyst
-   **Description**: User types a question into the Search Bar.
-   **System Action**:
    1.  React sends query to Backend.
    2.  Backend Agent interprets question.
    3.  Generates SQL -> Fetches Data.
    4.  Synthesizes Answer.
    5.  React displays answer and data table.

#### **UC-02: Filtered Data Exploration**
-   **Actor**: Analyst
-   **Description**: User selects "Rafael Nadal", "Clay", "2005-2020".
-   **System Action**:
    1.  React calls `/api/matches?player=Nadal&surface=Clay...`
    2.  Backend queries Database.
    3.  Returns structured JSON list of matches.
    4.  React renders sortable table.

#### **UC-03: View Player Profile**
-   **Actor**: Any User
-   **Description**: Detailed view of a specific player's stats.
-   **System Action**: Fetch metadata + aggregate stats (W/L record, Titles) from API.

### **System Maintenance**

#### **UC-04: Database Update**
-   **Actor**: Admin
-   **Description**: Ingest new match data.
-   **System Action**: Python scripts parse CSV/ATP data sources and update SQLite/Cloud SQL.

## 🔄 Interaction Flow (Example)

**Scenario: Analyst researching "Big 3" Head-to-Head**
1.  Analyst opens App.
2.  **UC-01**: Types "Federer vs Nadal vs Djokovic stats".
3.  System recognizes comparison intent.
4.  System displays comparison table.
5.  **UC-02**: Analyst filters by "Grand Slams only".
6.  Table updates to show only Major matches.
