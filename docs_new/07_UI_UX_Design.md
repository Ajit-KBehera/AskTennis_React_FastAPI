# 🎨 AskTennis AI - UI/UX Design Information

## Overview

The AskTennis AI system features a modern, intuitive user interface built with **React 19**, **TypeScript**, and **Tailwind CSS 4**. The design emphasizes responsiveness, accessibility, type safety, and visual appeal, offering a seamless experience for tennis analytics.

## 🎯 Design Philosophy

### 1. **User-Centered Design**
-   **Intuitive Navigation**: Easy-to-use interface for all user types (casual fans, analysts).
-   **Accessibility**: Support for keyboard navigation, screen readers, and high contrast.
-   **Responsive Design**: CSS Media queries ensure layout adaptation for mobile, tablet, and desktop.
-   **Performance**: Fast loading via Vite 7 bundler and optimistic UI updates.
-   **Type Safety**: TypeScript ensures compile-time error detection and better developer experience.

### 2. **Visual Design Principles**
-   **Clean Aesthetics**: Minimalist design with clear visual hierarchy.
-   **Consistent Branding**: Cohesive color scheme defined in Tailwind CSS 4 configuration.
-   **Typography**: Readable fonts with proper line height and spacing.
-   **Dark Mode**: Dark theme optimized for extended use (primary theme).

### 3. **Modern Tech Stack**
-   **React 19**: Latest React features for optimal performance.
-   **TypeScript**: Type safety throughout the application.
-   **Tailwind CSS 4**: Utility-first CSS framework for rapid development.
-   **Zustand**: Lightweight state management.
-   **Recharts & Plotly**: Rich data visualizations.

## 🎯 Application Interface Design

### 🎨 **Frontend Architecture** (`frontend/src/`)

**Entry Point**: `main.tsx` → `App.tsx`

**Component Structure:**
```
App.tsx (Root)
├── AuthContext (Authentication Provider)
│   └── Login Component (if not authenticated)
│
└── Layout Component (if authenticated)
    ├── Header Component
    │   ├── Logo & Title
    │   └── User Menu (Logout)
    │
    ├── Sidebar Component (Optional)
    │   └── Navigation Links
    │
    └── Main Content Area
        ├── SearchPanel Component
        │   ├── Input Field (Natural Language)
        │   ├── Microphone Button (Voice input via Web Speech API; transcript fills input)
        │   ├── Quick Insights (Suggested Queries)
        │   └── Submit Button
        │
        ├── FilterPanel Component (Optional)
        │   ├── Player Select (AsyncSelect)
        │   ├── Tournament Select
        │   ├── Surface Checkboxes
        │   ├── Year Selector
        │   └── Apply Button
        │
        └── Results Area
            ├── AiResponseView Component
            │   ├── Answer Card (Markdown Rendered)
            │   ├── Data Tables (MatchesTable)
            │   ├── SQL Code Block (Expandable)
            │   └── Conversation Flow (Debug)
            │
            └── StatsDashboardView Component
                ├── Stats Charts (StatsChart)
                ├── Player Profile
                └── Ranking History
```

## 🎨 Visual Design System

### 1. **Color Palette** (Tailwind CSS 4)

**Primary Colors:**
- **Background**: `bg-[#0f172a]` (Dark slate)
- **Surface**: `bg-slate-800` (Card backgrounds)
- **Primary**: `bg-blue-600` (Actions, links)
- **Accent**: `bg-green-500` (Success states)
- **Error**: `bg-red-500` (Error states)
- **Warning**: `bg-yellow-500` (Warnings)

**Text Colors:**
- **Primary Text**: `text-white` / `text-slate-100`
- **Secondary Text**: `text-slate-400`
- **Muted Text**: `text-slate-500`

**Border Colors:**
- **Default**: `border-slate-700`
- **Focus**: `border-blue-500`
- **Error**: `border-red-500`

### 2. **Typography System**

**Font Families:**
- **Body**: System font stack (sans-serif)
- **Code**: Monospace font for SQL/code blocks
- **Headings**: Bold, clear hierarchy

**Font Sizes:**
- **H1**: `text-4xl` (Page titles)
- **H2**: `text-3xl` (Section titles)
- **H3**: `text-2xl` (Subsection titles)
- **Body**: `text-base` (Default)
- **Small**: `text-sm` (Captions, metadata)
- **Code**: `text-sm font-mono` (SQL blocks)

### 3. **Spacing System**

Using Tailwind's spacing scale:
- **xs**: `p-2` (Tight spacing)
- **sm**: `p-4` (Small spacing)
- **md**: `p-6` (Medium spacing)
- **lg**: `p-8` (Large spacing)
- **xl**: `p-12` (Extra large spacing)

### 4. **Interactive States**

-   **Hover**: Subtle background shifts (`hover:bg-slate-700`)
-   **Active**: Visual feedback on clicks (`active:scale-95`)
-   **Focus**: Clear focus rings (`focus:ring-2 focus:ring-blue-500`)
-   **Disabled**: Opacity reduction (`opacity-50 cursor-not-allowed`)
-   **Loading**: Skeleton loaders and spinners (`TennisLoader`)

## 🎯 Component Design

### 1. **Login Component**

**Features:**
- Centered card layout
- Username and password inputs
- Submit button with loading state
- Error message display
- Link to registration (future)

**Styling:**
- Card with rounded corners (`rounded-lg`)
- Shadow for depth (`shadow-xl`)
- Focus states on inputs
- Responsive width (`max-w-md`)

### 2. **SearchPanel Component**

**Features:**
- Large text input for natural language queries
- Placeholder text with examples
- Submit button (or Enter key)
- Loading state during query
- Quick insights (suggested queries)

**Styling:**
- Full-width input (`w-full`)
- Rounded input (`rounded-lg`)
- Focus ring (`focus:ring-2`)
- Icon buttons for actions

### 3. **FilterPanel Component**

**Features:**
- Dynamic loading: selecting a player updates available tournaments
- Multi-select for surfaces
- Year range selector
- Apply button or auto-apply on change

**Styling:**
- Card layout with padding
- Dropdowns with custom styling
- Checkboxes for multi-select
- Responsive grid layout

### 4. **AiResponseView Component**

**Features:**
- Markdown-rendered answer with KaTeX for math
- Expandable SQL code block with syntax highlighting
- Data tables with sorting and pagination
- Conversation flow debug view (expandable)

**Styling:**
- Card layout for answer
- Code block with dark theme
- Table with hover states
- Expandable sections with smooth transitions

### 5. **MatchesTable Component**

**Features:**
- Sortable columns
- Scrollable table (virtualized for performance)
- Row hover effects
- Responsive design (horizontal scroll on mobile)

**Styling:**
- Striped rows (`even:bg-slate-800`)
- Hover effects (`hover:bg-slate-700`)
- Sortable column indicators
- Fixed header on scroll

### 6. **StatsChart Component**

**Features:**
- Recharts integration for line/bar charts
- Plotly.js for advanced visualizations
- Responsive sizing
- Interactive tooltips

**Styling:**
- Chart container with padding
- Responsive width (`w-full`)
- Dark theme colors
- Custom tooltip styling

## 📱 Responsive Design

### 1. **Breakpoint System** (Tailwind CSS)

- **sm**: `640px` (Small tablets)
- **md**: `768px` (Tablets)
- **lg**: `1024px` (Desktop)
- **xl**: `1280px` (Large desktop)
- **2xl**: `1536px` (Extra large)

### 2. **Mobile-First Approach**

**Mobile (< 768px):**
- Stacked layout (Filters above content)
- Full-width components
- Collapsible sidebar
- Bottom navigation (optional)
- Touch-friendly buttons (min 44px)

**Tablet (768px - 1024px):**
- Side-by-side layout (Filters left, Content right)
- Medium-sized components
- Optimized spacing

**Desktop (> 1024px):**
- Full layout with sidebar
- Larger components
- More whitespace
- Hover states enabled

### 3. **Responsive Components**

**SearchPanel:**
- Mobile: Full width, stacked buttons
- Desktop: Centered, inline buttons

**FilterPanel:**
- Mobile: Collapsible accordion
- Desktop: Always visible sidebar

**Data Tables:**
- Mobile: Horizontal scroll, simplified columns
- Desktop: Full table with all columns

## 🎨 User Experience Flows

### 1. **Primary User Journey**

1.  User lands on app (login page if not authenticated).
2.  User logs in with credentials.
3.  App loads filters (players, tournaments).
4.  User types "Who is the GOAT?" in search bar.
5.  Loading spinner appears (TennisLoader).
6.  Answer appears with markdown formatting.
7.  Data table shows Grand Slam titles comparison.
8.  User can expand SQL query to see how answer was generated.

### 2. **Data Exploration Flow**

1.  User selects "Rafael Nadal" from Player dropdown.
2.  Tournament dropdown updates with Nadal's tournaments.
3.  User selects "Roland Garros" from Tournament dropdown.
4.  User checks "Clay" surface filter.
5.  User clicks "Apply" or filters auto-apply.
6.  Table updates to show all matches won by Nadal at RG on clay.
7.  User can sort by date, opponent, or score.

### 3. **Authentication Flow**

1.  User visits app (not authenticated).
2.  Login page displayed (Login or Register mode).
3.  User enters credentials; in Register mode, **username availability** is shown (debounced). Optional **Remember Me** on login.
4.  Loading state during authentication.
5.  Success: Redirect to main app (extended session if Remember Me was checked).
6.  Error: Display error message, allow retry.

## 🎯 Component Library

### **UI Primitives** (`components/ui/`)

1. **DataTable**: Reusable table component with sorting
2. **DataVisualizer**: Generic data visualization wrapper
3. **Expander**: Expandable/collapsible sections
4. **SqlCodeBlock**: Syntax-highlighted SQL display
5. **TennisLoader**: Custom loading spinner/tennis-themed loader

### **Layout Components** (`components/layout/`)

1. **Layout**: Main application layout wrapper
2. **Header**: Top navigation bar
3. **Sidebar**: Side navigation (optional)

### **View Components** (`components/views/`)

1. **AiResponseView**: Main query results view
2. **StatsDashboardView**: Statistics dashboard

### **Feature Components**

1. **SearchPanel**: Natural language query input (typed or **voice** via mic button using Web Speech API)
2. **QuickInsights**: Suggested queries
3. **MatchesTable**: Match data table
4. **StatsChart**: Statistical charts
5. **Login**: Authentication form (Remember Me, username availability check, password strength, accessibility)

## 🎨 Visual Design Details

### **Cards & Containers**
- Rounded corners (`rounded-lg`)
- Shadow for depth (`shadow-lg`)
- Padding for content (`p-6`)
- Background color (`bg-slate-800`)

### **Buttons**
- Primary: `bg-blue-600 hover:bg-blue-700`
- Secondary: `bg-slate-700 hover:bg-slate-600`
- Danger: `bg-red-600 hover:bg-red-700`
- Disabled: `opacity-50 cursor-not-allowed`

### **Inputs**
- Border: `border-slate-700`
- Focus: `focus:border-blue-500 focus:ring-2`
- Background: `bg-slate-900`
- Text: `text-white`

### **Loading States**
- Skeleton loaders for content
- Spinner for actions
- Progress indicators for long operations

## 🔍 Accessibility Features

### **Keyboard Navigation**
- Tab order follows visual flow
- Enter key submits forms
- Escape key closes modals
- Arrow keys navigate lists

### **Screen Reader Support**
- Semantic HTML elements
- ARIA labels where needed
- Alt text for images
- Role attributes for custom components

### **Visual Accessibility**
- High contrast text
- Focus indicators
- Error messages clearly displayed
- Loading states communicated

## 🎯 Key UI/UX Design Benefits

1. **Speed**: React 19's optimizations ensure snappy updates.
2. **Type Safety**: TypeScript prevents runtime errors.
3. **Modularity**: Reusable components ensure consistency.
4. **Scalability**: Easy to add new visualizations or features.
5. **Modern DX**: Vite 7 provides instant feedback during development.
6. **Responsive**: Works seamlessly across all device sizes.
7. **Accessible**: Built with accessibility in mind.
8. **Performance**: Optimized rendering and lazy loading.

---

## 🎨 Design System Summary

The AskTennis AI UI/UX design leverages modern web technologies (React 19, TypeScript, Tailwind CSS 4) to create a fast, accessible, and visually appealing interface. The component-based architecture ensures consistency and maintainability, while the responsive design provides an optimal experience across all devices. The dark theme and clean aesthetics reduce eye strain during extended use, making it ideal for data analysis and exploration.
