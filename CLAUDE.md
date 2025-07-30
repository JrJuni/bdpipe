# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **bdpipe** - a Business Development Pipeline application built with Python and SQLite3. It's a CRM system for managing companies, contacts, projects, and business development tasks with AI-powered email parsing capabilities.

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
```

### AI Model Configuration
The application requires GGUF model files for AI functionality:
1. Download GGUF models (currently using Midm-2.0-Mini-Instruct variants)
2. Place in `models/` directory
3. Update `MODEL_FILENAME` in `src/config.py` if needed
4. Available models: Q4_K_M, Q5_K_M, Q8_0 (Q8_0 is default for better quality)

## Architecture

### Core Architecture Pattern
The system uses a modular, transaction-safe architecture with clear separation of concerns:

- **Configuration Layer** (`config.py`): Single source of truth for paths and settings
- **Database Layer**: Three-tier approach:
  - Schema (`db_schema.py`): DDL and table creation
  - Operations (`db_operations.py`): CRUD with transaction safety
  - Queries (`db_queries.py`): Complex read operations and joins
- **AI Integration Layer** (`db_aiwizard.py`): LLM wrapper with JSON response parsing
- **Export Layer** (`db_export.py`): Excel generation with timestamp naming
- **Application Layer** (`main.py`): CLI interface with menu-driven operations

### Database Design
SQLite3 with 9 interconnected tables:
- **Users**: Authentication and ownership
- **Companies**: Client organizations with hierarchical data
- **Contacts**: People within companies (foreign key to Companies)
- **Projects**: Work engagements with company relationships
- **Tasks**: Action items linked to companies/contacts/projects
- **Invoices & Invoice_Items**: Billing with line-item detail
- **Products**: Service catalog
- **Project_Participants**: Many-to-many project assignments

### Transaction Safety Pattern
All database operations use the helper function pattern:
- Internal functions accept `cursor` objects (no commits)
- Public functions manage connections and transactions
- Automatic rollback on exceptions
- Parameterized queries for SQL injection prevention

### AI Integration Pattern
LLM integration uses structured prompts with JSON response extraction:
- Model loading with error handling and fallback
- Temperature settings optimized for consistent JSON output
- Stop tokens to prevent over-generation
- Safe JSON parsing with error recovery

## Key Files and Their Responsibilities

- `src/main.py`: CLI menu system with user interaction flow
- `src/config.py`: Centralized configuration (DB paths, model paths)
- `src/db_schema.py`: Database DDL and initialization logic
- `src/db_operations.py`: CRUD operations with transaction safety
- `src/db_queries.py`: Read-only queries and complex joins
- `src/db_export.py`: Excel export with pandas/openpyxl integration
- `src/db_aiwizard.py`: LLM wrapper for email/text analysis
- `src/crm_wizard.py`: AI-powered CRM assistance features

## Development Notes

### Code Conventions
- Korean language support in UI strings and comments
- Parameterized queries mandatory for all SQL operations
- Transaction-safe patterns using cursor objects
- Single source of truth for configuration values
- Timestamp-based naming for exports and logs

### Testing Approach
- No formal test framework currently implemented
- Manual testing via `python src/db_operations.py`
- Database operations can be tested individually
- AI functions include error handling for model loading failures

### File Organization
- All source code in `src/` directory
- Database files in `data/` directory
- Generated exports in `exports/` directory  
- Log files in `logs/` directory with date-based naming
- GGUF model files in `models/` directory