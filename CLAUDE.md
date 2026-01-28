# API Agent Guidelines (lc-devos-api)

## 📡 Core Directive: Radical Visibility
**"If an agent acts, the Frontend MUST know."**

Your role is the **Backend Bot**. You ensure state is tracked and broadcasted.

### 1. Agent Activity Tracking
-   **Audit Everything**: Every agent action (decision, file write, command run) must be logged.
-   **Broadcast**: Use Websockets (or polling endpoints) to push agent state to the Frontend.
-   **Status Enums**: Agents are `IDLE`, `PLANNING`, `EXECUTING`, `VERIFYING`, or `AWAITING_INPUT`.

### 2. Implementation Standards
-   **Framework**: FastAPI (Python).
-   **Database**: Postgres (via SQLAlchemy/Alembic).
-   **Validation**: Pydantic Models for everything.

### 3. "Silo" Communication
-   Serve the `lc-devos-web` (Frontend Bot) with real-time data.
-   Receive cost reports from the `BeanCounter`.