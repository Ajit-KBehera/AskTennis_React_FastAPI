# AskTennis iOS App

Native iOS app for **AskTennis Analytics**, matching the look and behavior of the web app. Uses the same GCP backend:

**Backend URL:** `https://asktennis-backend-147976075322.us-central1.run.app`

## Requirements

- Xcode 15+ (Swift 5.9+)
- iOS 17+
- macOS for building/simulator

## Setup

### Option A: Open the included Xcode project

1. Open **`ios/AskTennis.xcodeproj`** in Xcode.
2. Select the **AskTennis** scheme and a simulator or device.
3. Press **⌘R** to build and run.

### Option B: Create new project in Xcode and add sources

1. Open **Xcode** → **File** → **New** → **Project**.
2. Choose **iOS** → **App** → Next.
3. Set **Product Name** to `AskTennis`, **Interface** to **SwiftUI**, **Language** to **Swift**. Uncheck tests if you like → Next → Save (e.g. in the repo root or in `ios/`).
4. In the Project Navigator, delete the default `ContentView.swift` and `AskTennisApp.swift` (or replace their contents).
5. **File** → **Add Files to "AskTennis"…** and select the **`AskTennis`** folder from this repo (`ios/AskTennis`). Ensure **Copy items if needed** is unchecked and **Create groups** is selected. Add all `.swift` files and the `Assets.xcassets` folder.
6. In **Project** → **Target** → **General**, set **Minimum Deployments** to **iOS 17.0**.
7. Build and run (⌘R) on a simulator or device.

### Option C: Open from existing Xcode project

If you already have an `AskTennis.xcodeproj` in `ios/`:

1. Open `ios/AskTennis.xcodeproj` in Xcode.
2. Build and run (⌘R).

## Backend

The app is configured to use:

- **Base URL:** `https://asktennis-backend-147976075322.us-central1.run.app`

This is set in **`Config.swift`**. Auth uses the same cookie-based session as the web app (login → cookie stored by `URLSession` → sent on all `/api/*` and `/auth/me`, `/auth/logout` requests).

## Features

- **Login / Register** – Same validation and API as web.
- **Ask AI** – Natural language query, AI answer, optional SQL and data expanders, conversation flow.
- **Quick insights** – Suggested questions and “Surprise me”, recent queries.
- **UI** – Dark theme, slate background, emerald accents, glass-style panels.

The iOS app includes **only the AI query flow** (no filters/sidebar or Stats dashboard) to keep memory usage low and avoid the system killing the app.

## Project structure

```
ios/AskTennis/
├── AskTennisApp.swift      # App entry, auth gate, loading
├── Config.swift            # Backend base URL
├── Models/
│   └── Models.swift        # API request/response types
├── Services/
│   └── APIClient.swift     # HTTP client (cookie-based auth)
├── ViewModels/
│   ├── AuthViewModel.swift
│   └── AIQueryViewModel.swift
├── Views/
│   ├── LoginView.swift
│   ├── ContentView.swift   # Main layout: header, search, results
│   ├── HeaderView.swift
│   ├── SearchPanelView.swift
│   ├── QuickInsightsView.swift
│   └── AiResponseView.swift
└── Assets.xcassets
```

## Changing the backend URL

Edit **`Config.swift`** and set `backendBaseURL` to your backend base URL (no trailing slash, no `/api`):

```swift
static let backendBaseURL = URL(string: "https://your-backend.run.app")!
```

Then rebuild the app.
