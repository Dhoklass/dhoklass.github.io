# GlitchFix — Your Online PC Problem Solver

A full-stack web application for remote PC support, built with Flask + MySQL.

---

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python Flask
- **Database:** MySQL
- **Remote Support:** RustDesk (public client)

---

## Setup Instructions

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database
- Open MySQL (via XAMPP, MySQL Workbench, or CLI)
- Run the schema file:
```sql
source schema.sql;
```

### 3. Configure Database Connection
Edit `config.py` and set your MySQL credentials:
```python
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''   # your MySQL password
MYSQL_DB = 'glitchfix_db'
```

### 4. Run the App
```bash
python app.py
```

Visit: `http://localhost:5000`

### 5. Load Sample Data
After the app is running, visit:
```
http://localhost:5000/seed
```
This creates all sample users, engineers, tickets, and updates.

---

## Demo Login Credentials (after seeding)

| Role     | Email                    | Password      |
|----------|--------------------------|---------------|
| Admin    | admin@glitchfix.com      | Admin@123     |
| Engineer | arjun@glitchfix.com      | Engineer@123  |
| Engineer | priya@glitchfix.com      | Engineer@123  |
| Engineer | rohan@glitchfix.com      | Engineer@123  |
| User     | amit@example.com         | User@123      |
| User     | sneha@example.com        | User@123      |
| User     | vijay@example.com        | User@123      |
| User     | kavya@example.com        | User@123      |

---

## Project Structure
```
glitchfix/
├── app.py                  # Main Flask application (all routes)
├── config.py               # Database & secret key config
├── requirements.txt        # Python dependencies
├── schema.sql              # MySQL database schema
├── README.md               # This file
├── static/
│   ├── css/
│   │   └── style.css       # Full dark theme stylesheet
│   └── js/
│       └── main.js         # Frontend interactivity
└── templates/
    ├── base.html           # Base layout
    ├── _alerts.html        # Flash message partial
    ├── _sidebar_user.html  # User sidebar
    ├── _sidebar_admin.html # Admin sidebar
    ├── _sidebar_engineer.html # Engineer sidebar
    ├── index.html          # Landing page
    ├── login.html          # Login (3 roles)
    ├── register.html       # User registration
    ├── user_dashboard.html # User dashboard
    ├── user_tickets.html   # User ticket list
    ├── create_ticket.html  # Raise new ticket
    ├── ticket_detail.html  # Ticket detail (shared across roles)
    ├── admin_dashboard.html
    ├── admin_tickets.html
    ├── admin_ticket_detail.html
    ├── admin_engineers.html
    ├── admin_users.html
    ├── engineer_dashboard.html
    ├── profile.html
    ├── about.html
    ├── faq.html
    └── contact.html
```

---

## RustDesk Remote Support Workflow
1. User installs RustDesk (free) from rustdesk.com
2. User notes their RustDesk ID and sets a temporary password
3. User includes RustDesk ID + password when raising a ticket
4. Admin assigns a certified engineer to the ticket
5. Engineer sees RustDesk credentials in the ticket detail page
6. Engineer opens RustDesk on their machine and connects to the user
7. Issue is fixed remotely — engineer marks ticket as Resolved
8. User is notified and can see the fix summary on their ticket

---

## Features
- 3 separate login roles: User, Admin, Engineer
- Full ticket lifecycle: Open → Assigned → In Progress → Resolved
- Activity timeline on every ticket
- Admin: assign engineers, update status, message users, delete tickets
- Engineer: view assigned tickets, update status, send messages, resolve tickets
- RustDesk ID/password stored per ticket for secure remote sessions
- Notifications system for users
- Sample data via /seed endpoint
- Responsive dark UI with animated counters
