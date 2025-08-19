# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **bdpipe** - a Business Development Pipeline application built with Python and SQLite3. It's a CRM system for managing companies, contacts, projects, and business development tasks with AI-powered email parsing capabilities and user authentication.

## Development Commands

### Environment Setup
```bash
# Install dependencies (supports both Windows/Linux)
pip install -r requirements.txt

# Initialize database schema
python src/db_schema.py

# Check database operations (manual testing)
python src/db_operations.py
```

### Running the Application
```bash
# Main CLI application with interactive menu
python src/main.py

# Streamlit web interface with authentication
streamlit run src/streamlit_app.py

# Alternative Streamlit app (older version)
streamlit run src/st_app.py
```

### AI Model Configuration
The application requires GGUF model files for AI functionality:
1. Download GGUF models (currently using Midm-2.0-Mini-Instruct variants)
2. Place in `models/` directory
3. Update `MODEL_FILENAME` in `src/config.py` if needed
4. Available models: Q4_K_M, Q5_K_M, Q8_0 (Q4_K_M is currently default)

### User Authentication Setup
On first run, the system creates an admin account:
- **Username**: `admin`
- **Password**: `admin0417`
- **Level**: 5 (Administrator)

User levels: 0=Pending, 1=User, 2=Approved, 3=Advanced, 4=Manager, 5=Admin

## Architecture

### Core Architecture Pattern
The system uses a modular, transaction-safe architecture with clear separation of concerns:

- **Configuration Layer** (`config.py`): Single source of truth for paths and settings
- **Database Layer**: Three-tier approach:
  - Schema (`db_schema.py`): DDL and table creation
  - Operations (`db_operations.py`): CRUD with transaction safety
  - Queries (`db_queries.py`): Complex read operations and joins
- **Authentication Layer** (`user_auth.py`): User management, password hashing, authorization levels
- **Web Interface Layer** (`streamlit_app.py`): Modern web UI with session management and role-based access
- **AI Integration Layer** (`ai_email.py`, `ai_greeting.py`): LLM wrapper with JSON response parsing
- **Export Layer** (`db_export.py`): Excel generation with timestamp naming
- **Application Layer** (`main.py`): CLI interface with menu-driven operations

### Database Design
SQLite3 with interconnected tables supporting full CRM workflow:
- **Users**: Authentication with username, password_hash, auth_level (0-5), soft deletion
- **Companies**: Client organizations with hierarchical data
- **Contacts**: People within companies (foreign key to Companies)
- **Projects**: Work engagements with company relationships
- **Tasks**: Action items linked to companies/contacts/projects with status tracking
- **Invoices & Invoice_Items**: Billing with line-item detail
- **Products**: Service catalog with pricing
- **Project_Participants**: Many-to-many project assignments
- **Free_Trials, Tech_Inquiries**: Specialized tracking tables

### Transaction Safety Pattern
All database operations use the helper function pattern:
- Internal functions accept `cursor` objects (no commits)
- Public functions manage connections and transactions
- Automatic rollback on exceptions
- Parameterized queries for SQL injection prevention

### Authentication & Authorization Pattern
Multi-level user system with role-based access control:
- SHA256 password hashing with salt-free approach
- Session token management for web interface persistence
- URL parameter-based session restoration for browser refresh
- Admin panel for user approval and level management
- Soft deletion for user accounts (is_deleted flag)

### Web Interface Pattern
Streamlit-based modern interface with:
- Tab-based login/registration system
- Session state management across page refreshes
- Role-based UI component visibility
- Debug mode toggle for development
- Password verification modal for sensitive operations

### AI Integration Pattern
LLM integration uses structured prompts with JSON response extraction:
- Model loading with error handling and fallback
- Temperature settings optimized for consistent JSON output
- Stop tokens to prevent over-generation
- Safe JSON parsing with error recovery

## Key Files and Their Responsibilities

- `src/main.py`: CLI menu system with comprehensive CRM operations
- `src/streamlit_app.py`: Modern web interface with authentication and admin panel
- `src/user_auth.py`: Complete authentication system with user management
- `src/config.py`: Centralized configuration (DB paths, model paths)
- `src/db_schema.py`: Database DDL and initialization logic
- `src/db_operations.py`: CRUD operations with transaction safety
- `src/db_queries.py`: Complex read operations and analytical joins
- `src/db_export.py`: Excel export with pandas/openpyxl integration
- `src/ai_email.py`: LLM wrapper for email/text analysis
- `src/ai_greeting.py`: AI greeting and interaction handling
- `src/st_app.py`: Alternative/legacy Streamlit interface

## Development Notes

### Code Conventions
- Korean language support in UI strings and comments
- Parameterized queries mandatory for all SQL operations
- Transaction-safe patterns using cursor objects
- Single source of truth for configuration values
- Timestamp-based naming for exports and logs

### Authentication Development Notes
- Default admin account created on first run: `admin`/`admin0417`
- User registration requires admin approval (Level 0 → Level 1+)
- Password changes require current password verification
- Email field supports NULL values (converted from empty strings)
- Deleted users have username modified with timestamp to allow reuse

### Testing Approach
- No formal test framework currently implemented
- Manual testing via `python src/db_operations.py`
- Database operations can be tested individually
- AI functions include error handling for model loading failures
- Web interface testing via `streamlit run src/streamlit_app.py`

### File Organization
- All source code in `src/` directory
- Database files in `data/` directory (mobilint_crm.db)
- Generated exports in `exports/` directory  
- Log files in `logs/` directory with date-based naming
- GGUF model files in `models/` directory
- Output files in `output/` directory

### Key Dependencies
Core packages from requirements.txt:
- `llama_cpp_python==0.3.12`: LLM integration via llama.cpp
- `pandas==2.3.1` & `openpyxl==3.1.5`: Excel export functionality
- `streamlit==1.47.0`: Web interface framework with session management
- `numpy==2.2.6`: Numerical operations
- Standard Python libraries for database, file operations