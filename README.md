
This is a Django REST Framework API for a productivity app that:
- Accepts a goal and uses AI to generate tasks/subtasks
- Supports goal and task management
- Manages events via a calendar system
- Supports team collaboration
- Offers user preferences onboarding

---

## 📡 API Overview

### 🔍 Dashboard Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/overview/` | Returns dashboard summary (progress, overdue, etc.) |
| `GET` | `/dashboard/<goalId>/goal_detail/` | Returns detailed data for a specific goal |
| `GET` | `/dashboard/goal-progress/` | Returns goal completion stats |

---

### 🎯 Task Manager Endpoints

#### Goals
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/taskmanager/goals/` | List all user goals |
| `GET` | `/taskmanager/goals/<goalId>/` | Retrieve a specific goal |
| `POST` | `/taskmanager/generate-subtasks/` | AI-generated subtasks from goal description |
| `PATCH` | `/taskmanager/goals/<goalId>/` | Update goal info |

#### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/taskmanager/tasks/<goalId>` | List all tasks for a goal |
| `POST` | `/taskmanager/tasks/` | Create a new task |
| `PATCH` | `/taskmanager/tasks/delete/<taskId>/` | Soft delete/edit task (custom route) |
| `PATCH` | `/taskmanager/tasks/<taskId>/complete/` | Mark task as complete |
| `DELETE` | `/taskmanager/tasks/<taskId>/` | Delete task |

#### Subtasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/taskmanager/subtasks/add/` | Add a subtask |
| `PATCH` | `/taskmanager/subtasks/edit/<subtaskId>/` | Edit a subtask |
| `DELETE` | `/taskmanager/subtasks/<subtaskId>/` | Delete subtask |

---

### 📅 Calendar Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/taskmanager/calendar/` | List scheduled events/tasks |
| `POST` | `/calendar/` | Create a new calendar event |
| `PATCH` | `/calendar/<eventId>/` | Update calendar event |
| `DELETE` | `/calendar/<eventId>/` | Delete calendar event |

---

### 👥 Team Collaboration Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/teams/` | List all teams user belongs to |
| `POST` | `/teams/` | Create a new team |
| `POST` | `/teams/<teamId>/invite/` | Invite user by email and role |
| `POST` | `/teams/accept-invite/<token>/` | Accept invite with a token |

---

### ⚙️ User Preferences (Onboarding)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/onboarding/` | Get current user preferences |
| `PUT` | `/onboarding/` | Update onboarding preferences |

---

## 🛠️ Development Setup

```bash
# Clone repo
git clone https://github.com/yourusername/taskbreaker-backend.git
cd taskbreaker-backend

# Setup virtual environment
python -m venv venv
source venv
