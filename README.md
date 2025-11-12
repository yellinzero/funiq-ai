# Funiq AI

Funiq AI is a personal research and learning project aimed at exploring the design and implementation of a modern AI workflow management platform. It strives to create a simplified and user-friendly ecosystem for creating, using, sharing, and managing AI agents, offering a flexible, powerful, and easily maintainable platform for AI applications.

## 🎯 Vision

Dedicated to lowering the barriers to AI application development, making AI technology more accessible to everyone. Through standardized development frameworks and intuitive interfaces, we aim to democratize AI technology and make it more practical for everyday use.

## ✅ Completed Features

### Backend

- ✅ **Workflow Engine Framework**
  - Complete workflow execution engine with lifecycle management
  - Support for workflow creation, execution, and debugging
  - Stream output support for real-time workflow execution results
  - Workflow versioning and publishing system
  - Debug snapshot management for workflow troubleshooting

- ✅ **Execution Logging System**
  - Structured workflow execution logging (`WorkflowLogger`)
  - File-based and database log storage
  - Real-time log streaming for debugging
  - Log lifecycle management with automatic cleanup

- ✅ **Model Provider System**
  - Dynamic model provider loading (Anthropic, OpenAI, DeepSeek)
  - Provider factory pattern for extensibility
  - Unified model configuration schema
  - Model parameter validation and schema generation

- ✅ **Operator System**
  - Extensible operator framework for workflow nodes
  - Built-in operators: Start, LLM, End
  - Dynamic operator loading and registration
  - Operator schema generation with i18n support

- ✅ **Multi-language Support (i18n)**
  - Backend internationalization with Babel
  - Translation support for Chinese and English
  - Automatic translation domain registration
  - Provider and operator schema translations

- ✅ **Module System**
  - Custom app module management system (`AppManager`)
  - Dynamic module loading and registration
  - Modular authentication and account management
  - RESTful API design with FastAPI

### Frontend

- ✅ **Visual Workflow Editor**
  - React Flow-based drag-and-drop workflow editor
  - Node types: Start, LLM, End (extensible)
  - Edge connection validation
  - Real-time workflow preview

- ✅ **Real-time Collaboration**
  - Yjs-based real-time sync for multi-user editing
  - WebSocket connection for live updates
  - User presence awareness (online users, cursor tracking)
  - Conflict resolution for concurrent edits

- ✅ **Workflow State Management**
  - Zustand-based workflow state management
  - Undo/redo support with Yjs UndoManager
  - Node and edge CRUD operations
  - Version history tracking

- ✅ **API Integration**
  - Type-safe API client with `openapi-fetch`
  - Auto-generated TypeScript types from OpenAPI schema
  - React Query for data fetching and caching
  - API error handling and validation

- ✅ **Internationalization**
  - i18next integration for multi-language support
  - Language detection and switching
  - Translation resources for Chinese and English

## 🚧 In Progress / Planned Features

### Backend

- [ ] **Workflow Execution Optimization**
  - Advanced error handling and retry mechanisms
  - Parallel execution support for independent nodes
  - Execution performance monitoring and metrics

- [ ] **Additional Operators**
  - Conditional operators (if/else, switch)
  - Loop operators (for, while)
  - Data transformation operators
  - HTTP request operators
  - Database query operators

- [ ] **Advanced Model Features**
  - Model response caching
  - Token usage tracking and cost management
  - Model performance comparison
  - Custom model provider integration

- [ ] **Workflow Templates**
  - Pre-built workflow templates
  - Template marketplace
  - Template import/export

- [ ] **User Management Enhancement**
  - Role-based access control (RBAC)
  - Team collaboration features
  - Workspace management

### Frontend

- [ ] **Workflow Execution Interface**
  - Real-time execution status visualization
  - Execution logs viewer
  - Execution history and replay
  - Debugging interface with breakpoints

- [ ] **Advanced Editor Features**
  - Minimap for large workflows
  - Node search and filtering
  - Workflow auto-layout
  - Node grouping and subflows
  - Copy/paste support

- [ ] **Data Visualization**
  - Node execution time visualization
  - Token usage charts
  - Workflow performance metrics dashboard

- [ ] **User Experience**
  - Onboarding tutorial
  - Interactive help system
  - Keyboard shortcuts
  - Accessibility improvements

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL 15+ with SQLAlchemy ORM
- **Cache**: Redis 6
- **Task Queue**: Celery
- **Package Manager**: Poetry
- **Code Quality**: Ruff (linting & formatting)
- **i18n**: Babel

### Frontend
- **Framework**: Next.js 15 (React 19)
- **UI Library**: Shadcn UI + Tailwind CSS 4
- **State Management**: Zustand + React Query 5
- **Workflow Editor**: React Flow (`@xyflow/react`)
- **Real-time Sync**: Yjs + y-websocket
- **Forms**: React Hook Form + Zod + `@rjsf/shadcn`
- **i18n**: i18next + react-i18next
- **Package Manager**: pnpm

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.10+, Poetry, Docker & Docker Compose
- **Frontend**: Node.js 18+, pnpm 9.12.2+

### Backend Setup
```bash
cd backend
cp .env.example .env
make up                    # Build and start all services
make db-setup             # Run migrations and initialize data
```

Backend will be available at:
- API Server: http://localhost:5001
- API Docs: http://localhost:5001/docs

### Frontend Setup
```bash
cd frontend
cp .env.example .env
pnpm install
pnpm dev                  # Start development server
pnpm start:ws
```

Frontend will be available at: http://localhost:3000

## 📚 Documentation

- [Frontend Documentation](./frontend/README.md)
- [Backend Documentation](./backend/README.md)
- [Development Guide](./CLAUDE.md)

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome! Feel free to:
- Open issues for bug reports or feature requests
- Submit pull requests for improvements
- Share your ideas and use cases

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
