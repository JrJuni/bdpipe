# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **bdpipe** - a Business Development Pipeline application built with Python and SQLite3. It's a CRM system for managing companies, contacts, projects, and business development tasks with AI-powered email parsing capabilities.

## Architecture

### Core Components
- **Database Layer**: SQLite3 with comprehensive CRM schema (9 tables)
  - Companies, Contacts, Projects, Tasks, Invoices, Products, Users
  - Proper foreign key relationships and constraints
- **AI Integration**: Uses llama.cpp with local GGUF models for email parsing and analysis
- **Export System**: Excel export functionality for data visualization
- **Configuration Management**: Centralized config system with paths and model settings

### Key Files
- `src/main.py`: CLI-based main application with menu system
- `src/config.py`: Project configuration and path management
- `src/db_schema.py`: Database initialization and table creation
- `src/db_operations.py`: CRUD operations for all entities
- `src/db_queries.py`: Complex queries and data retrieval
- `src/db_export.py`: Excel export functionality
- `src/db_aiwizard.py`: LLM integration for email parsing
- `src/crm_wizard.py`: AI-powered CRM assistance

### Database Schema
The system uses a relational schema with:
- Users (authentication and ownership)
- Companies (client organizations)
- Contacts (people within companies)
- Projects (work engagements)
- Tasks (action items and follow-ups)
- Invoices & Invoice_Items (billing)
- Products (service catalog)
- Project_Participants (many-to-many relationships)

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python src/db_schema.py
```

### Running the Application
```bash
# Main application
python src/main.py

# Database operations testing
python src/db_operations.py
```

### AI Model Setup
- Place GGUF model files in `models/` directory
- Configure model path in `src/config.py`
- Currently configured for: `Midm-2.0-Mini-Instruct-Q8_0.gguf`

## Project Structure

```
bdpipe/
├── data/               # SQLite database files
├── exports/           # Generated Excel files
├── logs/              # Application logs
├── models/            # GGUF model files for AI
├── output/            # Processing outputs
├── src/               # Source code
└── requirements.txt   # Python dependencies
```

## Key Dependencies
- `llama_cpp_python`: Local LLM inference
- `pandas`: Data manipulation
- `openpyxl`: Excel file generation
- `streamlit`: Web interface (planned/experimental)
- `sqlite3`: Built-in database

## Development Notes
- All database operations use parameterized queries for security
- AI parsing functions return structured JSON responses
- Excel exports include timestamp-based filenames
- Configuration uses single source of truth pattern
- Korean language support in UI and comments