# 🎨 AskTennis AI - UI/UX Design Information

## Overview

The AskTennis AI system features a modern, intuitive user interface built with **React** and **Vite**. The design emphasizes responsiveness, accessibility, and visual appeal, offering a seamless experience for tennis analytics.

## 🎯 Design Philosophy

### 1. **User-Centered Design**
-   **Intuitive Navigation**: Easy-to-use interface for all user types.
-   **Accessibility**: Support for high contrast and keyboard navigation.
-   **Responsive Design**: CSS Media queries ensure layout adaptation for mobile, tablet, and desktop.
-   **Performance**: Fast loading via Vite bundler and optimistic UI updates.

### 2. **Visual Design Principles**
-   **Clean Aesthetics**: Minimalist design with clear visual hierarchy.
-   **Consistent Branding**: Cohesive color scheme defined in `index.css` via CSS variables.
-   **Typography**: Readable fonts (system default or configured web fonts).

## 🎯 Application Interface Design

### 🎨 **Frontend Architecture** (`frontend/src/`)
-   **Entry Point**: `main.jsx` -> `App.tsx`
-   **Layout**: `Layout.tsx` (or similar container) orchestrating the main view.
-   **Key Components**:
    -   **`FilterPanel`**:
        -   Dropdowns for Player, Tournament, Surface.
        -   Dynamic loading of options via API calls.
    -   **`SearchPanel`**:
        -   Chat-like input for natural language queries.
        -   "Send" button with loading state.
    -   **`ResultsPanel`**:
        -   Displays the AI-generated answer.
        -   Renders data tables for structured match data.
        -   Expandable "Debug" section for SQL queries.

## 🎨 UI/UX Design Diagram

### **Component Hierarchy**
```
App (Root)
└── MainContainer
    ├── Header (Logo & Title)
    ├── ContentArea (Grid System)
    │   ├── LeftPanel (Filters)
    │   │   ├── PlayerSelect (AsyncSelect)
    │   │   ├── TournamentSelect
    │   │   ├── SurfaceSelect
    │   │   └── ApplyButton
    │   └── RightPanel (Interaction)
    │       ├── SearchBar
    │       │   ├── InputField
    │       │   └── ActionButtons
    │       └── ResultsArea
    │           ├── LoadingSpinner (Skeleton Loader)
    │           ├── AnswerCard (Text Response)
    │           ├── MetadataExpander (SQL & Reasoning)
    │           └── DataTable (Match Statistics)
    └── Footer
```

## 🎨 Visual Design System

### 1. **Color Palette** (CSS Variables)
Defined in `index.css`:
-   `--primary-color`: Branding blue/green.
-   `--bg-color`: Application background (support for dark mode).
-   `--text-color`: Main content text.
-   `--surface-color`: Card backgrounds.

### 2. **Typography System**
-   **Headings**: Bold, clear hierarchy (H1 -> H6).
-   **Body**: Readable height/spacing for data density.

### 3. **Interactive States**
-   **Hover**: Subtle background shifts on buttons/rows.
-   **Active**: Visual feedback on clicks.
-   **Disabled**: Opacity reduction for unavailable actions.

## 🎯 Component Design

### 1. **Filter Panel**
-   Features dynamic loading: selecting a player updates the available tournaments and opponents.
-   Uses API endpoints: `/api/filters/players`, `/api/filters/tournaments`.

### 2. **Search Interface**
-   Supports "Enter" to submit.
-   Persists chat history (optional feature in `ResultsPanel`).

### 3. **Results Display**
-   **Data Tables**: Sortable and scrollable.
-   **Visualizations**: Charts (Bar/Line) using libraries like Recharts (if implemented).

## 📱 Responsive Design

### 1. **Breakpoint System**
-   **Mobile**: Stacked layout (Filters collapse into a modal or accordion).
-   **Desktop**: Side-by-side layout (Filters Left, Content Right).

### 2. **Mobile-First CSS**
-   Default styles target mobile.
-   `@media (min-width: 768px)` enables complex layouts.

## 🎨 User Experience Flows

### 1. **Primary User Journey**
1.  User lands on the app.
2.  Types "Who is the GOAT?" in the search bar.
3.  Loaders appear indicating AI processing.
4.  Answer appears with a table of Grand Slam titles.

### 2. **Data Exploration Flow**
1.  User selects "Rafael Nadal" from the Player dropdown.
2.  Selects "Roland Garros" from Tournament dropdown.
3.  Clicks "Apply".
4.  Table updates to show all matches won by Nadal at RG.

---

## 🎯 Key UI/UX Design Benefits
1.  **Speed**: React's Virtual DOM ensures snappy updates.
2.  **Modularity**: Reusable components (`Card`, `Button`, `Select`) ensure consistency.
3.  **Scalability**: Easy to add new visualizations or tabs.
4.  **Modern DX**: Vite provides instant feedback during development.
