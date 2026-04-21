
# Freelance Agent Project Memory

## Project Overview
An autonomous agent system designed to scrape freelance platforms (Kwork, Freelance.ru, FL.ru), match jobs with user skills, and generate personalized proposals using AI (Gemini).

## Architecture
- **freelance-agent/**: CLI tool (Node.js/TypeScript/Playwright) for scraping and processing jobs.
  - **Adapters**: Platform-specific logic for scraping (src/adapters).
  - **Services**: Core logic for browser management, database (SQLite), matching, and learning.
  - **Data**: Stores SQLite DB, logs, reports, and learning history.
- **dashboard/**: Web interface (Next.js/Tailwind) for viewing jobs and managing proposals.
  - **API Routes**: Interface with the shared SQLite database and Gemini API.
  - **Gemini Service**: Handles prompt engineering and AI response generation.

## Key Conventions
- **Scraping**: Emulates browser behavior without official APIs to avoid detection. No authentication is used for initial scraping to minimize risk.
- **Job Scoring**:
  - `skillMatchScore`: 0-1 based on profile.json skills.
  - `clarityScore`: 0-1 based on description quality.
- **Database**: Shared SQLite database located at `freelance-agent/data/db/freelance.db`.
- **Cross-Project Integration**: 
  - Dashboard uses `better-sqlite3` to read/write to the same DB as the agent.
  - Dashboard dynamically imports `LearningService` from the agent's `dist/` folder to update skills and history. Ensure `npm run build` is run in `freelance-agent` after changes.
- **Environment**: Dashboard requires `.env.local` with `GEMINI_API_KEY`.

## Tech Stack
- **Backend**: Node.js, TypeScript, Playwright, Better-SQLite3.
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Lucide Icons.
- **AI**: Google Gemini 2.0 Flash.

## Critical Files
- `PROJECT_SPECIFICATION_RU.md`: Detailed business requirements.
- `STATUS_2026-03-24.md`: Current implementation progress and known issues.
- `freelance-agent/config/profile.json`: User skills and thresholds.
- `dashboard/src/lib/gemini.ts`: AI prompt logic.
