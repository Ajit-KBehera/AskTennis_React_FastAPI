# 👤 AskTennis AI - Use Case Diagram

## Overview

This document outlines the primary actors and use cases for the AskTennis AI system, highlighting the interactions between users and the React 19 + FastAPI platform. The system supports multiple user types with varying levels of access and requirements.

## 🎭 Actors

### 1. **Tennis Analyst / Researcher**
-   **Goal**: Deep dive into historical data, complex statistical analysis.
-   **Behavior**: Uses complex filters, looks at raw data tables, exports results, compares players.
-   **Technical Skills**: Comfortable with data analysis, understands tennis statistics.
-   **Access Level**: Authenticated user with full access.

### 2. **Casual Fan**
-   **Goal**: Quick answers to trivia, fun facts about tennis.
-   **Behavior**: Uses natural language chat ("Who is the best player on grass?"), simple queries.
-   **Technical Skills**: Basic, prefers simple interface.
-   **Access Level**: Authenticated user with standard access.

### 3. **System Administrator**
-   **Goal**: Maintain system health, monitor performance, manage users.
-   **Behavior**: Monitors API logs, manages database updates, reviews security.
-   **Technical Skills**: Advanced, understands infrastructure.
-   **Access Level**: Admin privileges (future enhancement).

### 4. **Unauthenticated User**
-   **Goal**: Explore the system before signing up.
-   **Behavior**: Views public information, attempts to access features.
-   **Access Level**: Limited or no access (redirected to login).

## 📋 Use Cases

### **Authentication & User Management**

#### **UC-01: User Registration**
-   **Actor**: Unauthenticated User
-   **Description**: User creates a new account with username and password.
-   **Preconditions**: User is not logged in.
-   **System Action**:
    1.  User navigates to registration page.
    2.  User enters username and password (min 8 characters).
    3.  React sends POST request to `/auth/register`.
    4.  Backend validates input (Pydantic schema).
    5.  Backend checks if username already exists.
    6.  Backend hashes password with bcrypt.
    7.  Backend stores user in authentication database.
    8.  Backend returns success response.
    9.  Frontend redirects to login page.
-   **Postconditions**: User account created, ready for login.
-   **Alternative Flow**: Username already exists → Error message displayed.

#### **UC-02: User Login**
-   **Actor**: Unauthenticated User
-   **Description**: User logs in with username and password.
-   **Preconditions**: User has registered account.
-   **System Action**:
    1.  User navigates to login page.
    2.  User enters username and password.
    3.  React sends POST request to `/auth/login`.
    4.  Backend validates credentials.
    5.  Backend verifies password hash.
    6.  Backend generates JWT token.
    7.  Backend sets HttpOnly cookie with JWT.
    8.  Backend updates last_login timestamp.
    9.  Backend returns success response.
    10. Frontend updates AuthContext with user info.
    11. Frontend redirects to main application.
-   **Postconditions**: User is authenticated, session established.
-   **Alternative Flow**: Invalid credentials → Error message displayed.

#### **UC-03: User Logout**
-   **Actor**: Authenticated User (Casual Fan, Analyst)
-   **Description**: User logs out of the system.
-   **Preconditions**: User is logged in.
-   **System Action**:
    1.  User clicks logout button.
    2.  Frontend clears AuthContext.
    3.  Frontend clears local state.
    4.  Backend invalidates session (optional, future enhancement).
    5.  Frontend redirects to login page.
-   **Postconditions**: User is logged out, session cleared.

### **Core Platform Functionality**

#### **UC-04: Natural Language Query**
-   **Actor**: Casual Fan, Analyst
-   **Preconditions**: User is authenticated.
-   **Description**: User types a question into the Search Bar.
-   **System Action**:
    1.  User types query in SearchPanel component.
    2.  React sends POST request to `/api/query` with:
        - `X-API-Key` header
        - `access_token` cookie (JWT)
        - Query text in request body
    3.  Backend validates API key.
    4.  Backend validates JWT token.
    5.  Backend checks rate limits.
    6.  Backend checks cache for query result.
    7.  If cache miss:
        a. Backend Agent interprets question.
        b. LangGraph agent processes query.
        c. Schema pruner optimizes context.
        d. LLM generates SQL query.
        e. Database executes SQL.
        f. LLM synthesizes natural language answer.
        g. Result stored in cache.
    8.  Backend returns JSON response with:
        - Answer text
        - SQL queries used
        - Data tables
        - Conversation flow
    9.  React displays answer in AiResponseView.
    10. React renders data tables.
    11. React shows SQL queries in expandable section.
-   **Postconditions**: Query answered, results displayed.
-   **Alternative Flow**: 
    - Rate limit exceeded → 429 error, retry message.
    - SQL error → Error message, agent may retry.
    - Network error → Toast notification with retry option.

#### **UC-05: Filtered Data Exploration**
-   **Actor**: Analyst
-   **Preconditions**: User is authenticated.
-   **Description**: User selects filters (player, tournament, surface, year) to refine data.
-   **System Action**:
    1.  User selects filters in FilterPanel component:
        - Player dropdown (async loaded)
        - Tournament dropdown
        - Surface checkboxes
        - Year selector
    2.  React calls `/api/filters/players` to load player options.
    3.  React calls `/api/filters/tournaments` to load tournament options.
    4.  User clicks "Apply Filters" or filter changes trigger update.
    5.  React calls `/api/matches` with filter parameters.
    6.  Backend validates filters.
    7.  Backend queries database with filters.
    8.  Backend returns structured JSON list of matches.
    9.  React renders sortable MatchesTable.
    10. User can sort columns, scroll through results.
-   **Postconditions**: Filtered data displayed.
-   **Alternative Flow**: No matches found → Empty state message.

#### **UC-06: View Player Statistics**
-   **Actor**: Any Authenticated User
-   **Preconditions**: User is authenticated.
-   **Description**: User views detailed statistics for a specific player.
-   **System Action**:
    1.  User queries "Show me Rafael Nadal's statistics" or selects player from filter.
    2.  React sends query to `/api/query` or `/api/stats/players`.
    3.  Backend fetches player metadata.
    4.  Backend aggregates statistics (W/L record, titles, rankings).
    5.  Backend returns player stats.
    6.  React displays StatsDashboardView with:
        - Player profile information
        - Win/loss statistics
        - Surface breakdown
        - Ranking history chart
        - Recent matches
-   **Postconditions**: Player statistics displayed.
-   **Alternative Flow**: Player not found → Error message.

#### **UC-07: View Match History**
-   **Actor**: Analyst
-   **Preconditions**: User is authenticated.
-   **Description**: User views historical match data with detailed statistics.
-   **System Action**:
    1.  User applies filters or queries "Show me matches between Federer and Nadal".
    2.  React calls `/api/matches` with parameters.
    3.  Backend queries matches table.
    4.  Backend returns match data with statistics.
    5.  React displays MatchesTable with:
        - Match details (date, tournament, surface)
        - Players (winner, loser)
        - Score
        - Match statistics (aces, double faults, etc.)
    6.  User can sort, filter, and export data.
-   **Postconditions**: Match history displayed.

#### **UC-08: View Rankings History**
-   **Actor**: Analyst
-   **Preconditions**: User is authenticated.
-   **Description**: User views ranking history for players.
-   **System Action**:
    1.  User queries "Show me Novak Djokovic's ranking history".
    2.  Backend queries rankings table.
    3.  Backend returns ranking data over time.
    4.  React displays ranking chart (line chart) showing:
        - Ranking position over time
        - Ranking points
        - Tournament count
    5.  User can compare multiple players.
-   **Postconditions**: Ranking history displayed.

### **System Maintenance**

#### **UC-09: Database Update**
-   **Actor**: Admin (System Administrator)
-   **Description**: Admin ingests new match data into the database.
-   **System Action**:
    1.  Admin prepares data file (CSV, JSON, or database dump).
    2.  Admin runs data import script or uses admin interface (future).
    3.  Script validates data format.
    4.  Script inserts/updates records in database.
    5.  Script updates indexes.
    6.  Script validates data integrity.
    7.  System logs update completion.
-   **Postconditions**: Database updated with new data.
-   **Alternative Flow**: Data validation fails → Error logged, partial rollback.

#### **UC-10: Monitor System Health**
-   **Actor**: Admin (System Administrator)
-   **Description**: Admin monitors system performance and health.
-   **System Action**:
    1.  Admin accesses monitoring dashboard (future) or logs.
    2.  System displays:
        - API request rates
        - Response times
        - Error rates
        - Cache hit rates
        - Database query performance
        - Active user sessions
    3.  Admin reviews OpenTelemetry traces.
    4.  Admin checks structured logs with request IDs.
    5.  Admin identifies performance bottlenecks.
-   **Postconditions**: System health assessed.

#### **UC-11: Manage Rate Limits**
-   **Actor**: Admin (System Administrator)
-   **Description**: Admin configures rate limits for API endpoints.
-   **System Action**:
    1.  Admin accesses configuration (environment variables or admin UI).
    2.  Admin sets rate limits per endpoint:
        - General API: 30 requests/minute
        - Query endpoint: 10 requests/minute
    3.  Configuration applied to rate limiter.
    4.  System enforces new limits.
-   **Postconditions**: Rate limits updated.

## 🔄 Interaction Flow (Example)

**Scenario: Analyst researching "Big 3" Head-to-Head**

1.  **UC-02**: Analyst logs in with credentials.
2.  **UC-04**: Types "Federer vs Nadal vs Djokovic stats" in search bar.
3.  System recognizes comparison intent.
4.  System displays comparison table with:
    - Head-to-head records
    - Grand Slam titles comparison
    - Surface breakdowns
5.  **UC-05**: Analyst filters by "Grand Slams only".
6.  Table updates to show only Major matches.
7.  **UC-07**: Analyst clicks on specific match to view details.
8.  **UC-08**: Analyst views ranking history for all three players.
9.  Analyst exports data for further analysis (future feature).

## 🎯 Use Case Relationships

### **Dependencies**
- UC-04, UC-05, UC-06, UC-07, UC-08 all require UC-02 (Login).
- UC-04 may trigger UC-05 (filtered exploration) based on query results.
- UC-06, UC-07, UC-08 can be accessed via UC-04 (natural language) or direct API calls.

### **Extension Points**
- **Future UC-12**: Export Data (extends UC-05, UC-07).
- **Future UC-13**: Compare Players (extends UC-06).
- **Future UC-14**: Save Queries (extends UC-04).
- **Future UC-15**: Share Results (extends UC-04, UC-05).

## 🛡️ Security Considerations

### **Authentication Required**
- All `/api/*` endpoints require authentication (UC-02).
- Unauthenticated users are redirected to login (UC-01).

### **Rate Limiting**
- UC-04 (Natural Language Query) is rate-limited to prevent abuse.
- UC-05 (Filtered Exploration) has higher rate limits.

### **Data Access**
- Users can only access their own session data.
- No cross-user data access (future: admin override).

---

## 🎯 Key Use Case Benefits

1. **User-Centric Design**: Use cases focus on user goals and behaviors.
2. **Security**: Authentication and authorization built into core flows.
3. **Flexibility**: Multiple ways to access data (natural language, filters, direct queries).
4. **Scalability**: Use cases designed for high user concurrency.
5. **Maintainability**: Clear separation of concerns enables easy updates.

This use case diagram provides a comprehensive view of how users interact with the AskTennis AI system, ensuring all user needs are addressed while maintaining security and performance.
