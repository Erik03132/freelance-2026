# Freelance Agent MVP — Project Specification

## 1. Goal and General Concept

Create an autonomous agent application that:

- On a schedule (e.g., daily at 09:00) visits selected freelance marketplaces (via browser interface, without official APIs).
- Finds new tasks, automatically matches them with my skill profile, and selects only suitable ones (skill match threshold ≥ 70%).
- Selects tasks with sufficiently detailed and clear specifications.
- For selected tasks, prepares pre-sales materials: prototype, demo, draft mockup, code fragment, etc.
- Generates a safe preview result (watermarks, partial functionality, deployment to my hosting, etc.) so the client cannot freely take the result.
- Notifies me about suitable tasks and, optionally, generates a draft proposal/response to the client.

---

## 2. Target Platforms and Legal Limitations

The agent must account for strict scraping and automation rules on major marketplaces (Upwork, Fiverr, Freelancer, etc.).

**Input data (parameters):**
- List of platforms: URLs of task feed pages (search, categories, filters).
- Authorization format: login/password, 2FA, cookies (entered manually by the user).

**Compliance requirements:**
- Use only browser emulation (Antigravity agent in browser): clicking, reading DOM, scrolling, without direct "scraping" requests bypassing the interface.
- Configure "human" delays, request rate limiting (to avoid blocking).
- Do not bypass paywalls, captchas, or technical protection measures.
- Provide a checkbox in settings: "I accept the risk and responsibility for automation on these sites" — the agent does not make decisions for the user.

---

## 3. Application Architecture and Operating Modes

The application should be built around the Antigravity agent approach, where agents can interact with the browser, editor, and terminal.

**Minimum modules:**

### 1) Scheduler Agent
- Runs on schedule (default: 09:00 daily).
- Starts the chain: authorization → platform browsing → parsing → filtering → pre-sales material generation.

### 2) Scraper Agent (Browser-Use)
- Works inside the browser: logs in, scrolls through task pages, opens project cards, extracts text descriptions, budget, deadlines, skill tags.
- Handles multiple platforms sequentially, but with a unified interface (each platform is a separate action scenario).

### 3) Matching Agent (Skill Match Evaluation)
- Compares task descriptions with my skill profile.
- Calculates "match percentage" based on: keywords, semantic similarity, skill categories.
- Selects only tasks where score ≥ specified threshold (e.g., 0.7 on a 0–1 scale).

### 4) TZ Quality Filter Agent
- Evaluates "completeness/clarity of specification" using heuristics:
  - Is the project goal described.
  - Are there technical details (stack, platforms, integrations, examples).
  - Are there input data/materials (mockups, examples, links).
- Assigns tasks a "clarity score" (0–1) and discards tasks below threshold (e.g., 0.6).

### 5) Solution-Draft Agent (Preliminary Solution)
- For each filtered task:
  - Generates a solution plan (structured technical solution).
  - If needed, creates a prototype:
    - If task is about website — scaffold project (e.g., Next.js/React), basic layout of key pages, mock data.
    - If task is about design — set of preview images with watermarks.
  - Prepares a "limited version" of the result, suitable for demonstration but not full use.

### 6) Protection Agent (Safety Measures)
- Implements protection measures against dishonest clients:
  - Web projects deployed to my hosting/server with limited functionality (e.g., no export, route restrictions, no source code).
  - Design and graphics — with watermarks (logo, email, text).
  - Code — only fragments/snippets, without full implementation of critical parts.
- Prepares a list of "what will be removed/unlocked only after payment" (to clearly communicate to the client).

### 7) Proposal Agent (Letter/Response Preparation)
- Generates a draft message to the client:
  - Briefly restates the task in own words.
  - Lists why I'm a good fit (skills, experience).
  - Attaches a link to demo/prototype.
  - Specifies payment format and next steps.
- Implemented so I can manually edit/approve the letter before sending.

### 8) UI Dashboard
- List of tasks found today: platform, title, budget, deadline, match percentage, TZ clarity.
- Statuses: "new", "prototype ready", "proposal sent", "in negotiation", "closed".
- Settings (see next section).

---

## 4. Profile and Skills Settings

A separate "Profile and Skills" block is required:

**Basic information:** name, nickname, portfolio links (GitHub, website, Dribbble, etc.).

**Skills list with levels:**
- Example: `React – 0.9, Next.js – 0.8, Node.js – 0.7, UI/UX – 0.6` (0–1 scale).

**Task categories of interest:**
- Web development, backend, integrations, design, landing pages, mobile apps, etc.

**Task types to ignore:**
- Copywriting, SMM, translation, "gray/suspicious" topics (tasks with keywords: "botnet", "carding", "spam", etc.).

**Matching settings:**
- Match score threshold (default 0.7).
- Weight of skills vs experience (if resume/portfolio import is implemented).
- Ability to manually exclude specific clients/keywords.

---

## 5. Task and TZ Matching Logic

### 5.1 Skill Matching

Use a combined approach:
- Dictionary/keyword (exact match of skills and stacks).
- Semantic similarity (synonyms, similar frameworks).

**Example logic:**
- Extract skills-tokens from task description.
- Match them with my skills list.
- For each matched skill, sum weights, normalize to maximum.
- Get final score ∈ [0, 1].

### 5.2 TZ Clarity/Quality Scoring

Introduce a simple "scoring model":

**Signs that increase score:**
- Technology stack specified.
- Examples/references provided.
- User scenarios described.
- Formal acceptance criteria specified.

**Signs that decrease score:**
- "Make a website somehow", "make it beautiful", "we'll figure it out along the way".
- Few details, only 1–2 sentences.

**Result:** `clarity_score` ∈ [0, 1]; applications below threshold are not sent to auto-prototype generation.

---

## 6. Protection Mechanisms Against Dishonest Clients

**General principles:**
- Demo should show competence but not provide a working "production" solution.
- Anything easily copied must be limited or protected.

**Specific measures:**

### 1) Web Projects
- Deploy only to my domain/hosting.
- No client access to repository/project archive.
- Critical parts (unique algorithms, integrations, infrastructure) — not implemented in demo or implemented as mocks.

### 2) Design/Graphics
- Automatic watermark overlay (logo, url, email) on all preview images.
- Low resolution preview (e.g., 1200 px on long side).

### 3) Code/Scripts
- Demonstrate structure and key ideas, but not full production code.
- Limit to fragments in message plus demo link.

### 4) Legal Disclaimers
- Standard text in message:
  - "This demo is provided for informational purposes only; rights to the solution and source code are transferred only after payment and contract signing."

---

## 7. Risk Management and Anti-Spam Logic

To avoid burning out clients and getting banned on platforms:

- **Daily task limits:**
  - Maximum X new tasks for prototype generation per day (X is configurable).
- **Auto-send limits:**
  - By default, the agent only prepares drafts and waits for my confirmation.
- **Message templates** must be personalized, referencing specific TZ details, to avoid looking like spam.
- **Built-in stop-word list** for tasks to ignore for ethical or legal reasons.

---

## 8. Antigravity Integration and Technical Requirements

Given that Antigravity is an IDE and agent programming platform with browser, editor, and terminal access:

**Agent must be able to:**
- Control browser: open tabs, log in, click, read HTML/DOM, scroll.
- Create/edit project files in local workspace (via IDE interface).
- Run deployment commands (e.g., `npm install`, `npm run build`, `npm run deploy` or Docker commands), if explicitly allowed.

**Guardrails required:**
- Logs of all agent actions.
- Ability to stop/pause the agent.
- Permission settings: which sites can be accessed, which terminal commands are allowed.

---

## 9. Minimum MVP and Priorities

**Development sequence (for the agent):**

### MVP #1 (Minimum Viable Product)
- One or two specific platforms.
- Login, collect tasks from last 24 hours.
- Simple filtering by keywords and manual skills list.
- Task list + letter drafts without prototypes.

### MVP #2
- Implement semantic skill matching (score ≥ 0.7).
- TZ clarity evaluation.
- Auto-generation of text solution plan and basic prototype (e.g., website template).

### MVP #3
- Protection measures (watermarks, demo deployment to own hosting).
- Expansion to multiple platforms.
- Full dashboard with filters and task statuses.

---

## 10. Additional Feature Requests

- **Ability to "fine-tune" the matcher** on my past projects:
  - Upload a list of tasks I successfully completed and those that don't fit, to improve the algorithm.
- **Reports:**
  - Weekly statistics — how many tasks found, how many prototypes made, how many responses sent, how many dialogues started.
- **Manual review mode:**
  - Ability to manually mark tasks as "interested/not interested" so the system can adapt.

---

## 11. References

- [Antigravity AI 2025](https://blog.meetneura.ai/antigravity-ai-2025/)
- [Skill Matching Research](https://www.sciencedirect.com/science/article/pii/S2214579625000048)
- [Freelance Platform Terms Comparison](https://quicktop10.com/blog/freelance-platform-terms-of-service-a-comparative-overview-october-11-2025/)
- [Skill Matching Academic Paper](https://bura.brunel.ac.uk/bitstream/2438/32657/1/FullText.pdf)
- [Fiverr vs Upwork Comparison 2025](https://www.uneversleep.com/blog/fiverr-vs-upwork-comparison-2025/)
- [Google Antigravity (Wikipedia)](https://en.wikipedia.org/wiki/Google_Antigravity)
