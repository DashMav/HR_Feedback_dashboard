---
title: Multi-Tenant HR Feedback System
emoji: 🏢
colorFrom: indigo
colorTo: gray
sdk: docker
pinned: false
license: mit
---

# Multi-Tenant HR Feedback System

A comprehensive, enterprise-grade feedback management system supporting multiple organizations with role-based access control, user invitations, and PostgreSQL backend.

## 🚀 Features

### Multi-Tenant Architecture
- **Organization Management**: Complete isolation between organizations
- **Role-Based Access Control**: Owner, Admin, Manager, and Employee roles
- **User Invitations**: Email-based invitation system with token validation
- **Data Security**: Organization-scoped data access and filtering

### Core Feedback Features
- **Structured Feedback**: Strengths, improvements, and sentiment tracking
- **Rich Text Support**: Markdown formatting for detailed feedback
- **Tag System**: Categorize feedback with custom tags
- **Employee Responses**: Two-way communication on feedback
- **Acknowledgment System**: Track feedback receipt and engagement

### User Management
- **Invitation System**: Secure email invitations with expiration
- **User Lifecycle**: Activation, suspension, and role management
- **Manager Hierarchy**: Support for reporting relationships
- **Activity Tracking**: Last login and engagement metrics

### Enterprise Features
- **PostgreSQL Backend**: Production-ready database with migrations
- **RESTful API**: Comprehensive API with OpenAPI documentation
- **Security**: JWT authentication, password hashing, CORS protection
- **Responsive Design**: Mobile-first UI with Tailwind CSS

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with JSON support
- **SQLAlchemy**: ORM with Alembic migrations
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Authorization**: Granular permission system

### Frontend (Next.js + React)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Responsive Design**: Mobile and desktop optimized

## 🚀 Quick Start

### Demo Access
Try the system with pre-configured demo accounts:

**Demo Company Organization:**
- **Owner**: owner@demo.com / password123
- **Manager**: manager@demo.com / password123  
- **Employee**: employee@demo.com / password123

### Setting Up New Organization

1. **Visit Setup Page**: Go to `/setup` to create a new organization
2. **Create Organization**: Enter organization name and optional email domain
3. **Create Admin Account**: Set up the first user as organization owner
4. **Invite Team Members**: Use the admin dashboard to invite users

## 📊 User Roles & Permissions

### Organization Owner
- Full system access within organization
- User management and role assignment
- Organization settings and configuration
- All feedback management capabilities

### Admin
- User management within organization
- Invite and manage team members
- View organization-wide analytics
- Feedback oversight and reporting

### Manager
- Manage direct reports
- Give feedback to team members
- View team performance metrics
- Access feedback history for reports

### Employee
- Receive and acknowledge feedback
- Comment on received feedback
- View personal feedback history
- Update profile information

## 🔧 Technical Implementation

### Database Schema

#### Organizations Table
- Multi-tenant data isolation
- Optional email domain for auto-assignment
- Organization-level settings and configuration

#### Users Table
- Unique email per organization constraint
- Role-based access control
- Manager hierarchy support
- Activity tracking

#### Invitations Table
- Secure token-based invitations
- Expiration handling
- Role pre-assignment
- Audit trail

#### Feedback Table
- Organization-scoped data
- Rich content with JSON tags
- Sentiment tracking
- Employee engagement metrics

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User authentication with organization context
- `POST /api/auth/register` - First user registration for organization
- `GET /api/auth/me` - Current user information

#### Organization Management
- `POST /api/organizations` - Create new organization
- `GET /api/organizations` - List available organizations
- `GET /api/organizations/{id}` - Organization details

#### User Management
- `GET /api/users` - List organization users (admin only)
- `PUT /api/users/{id}` - Update user details (admin only)
- `POST /api/invitations` - Send user invitation
- `GET /api/invitations` - List pending invitations
- `POST /api/invitations/accept` - Accept invitation

#### Feedback System
- `POST /api/feedback` - Create feedback
- `GET /api/feedback/received` - Employee's received feedback
- `GET /api/feedback/employee/{id}` - Feedback history for employee
- `POST /api/feedback/{id}/acknowledge` - Acknowledge feedback
- `POST /api/feedback/{id}/comment` - Add employee comment

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: Bcrypt with salt for password security
- **Role-Based Access**: Granular permissions by user role
- **Organization Isolation**: Complete data separation between organizations

### Data Protection
- **Input Validation**: Comprehensive request validation with Pydantic
- **SQL Injection Prevention**: ORM-based queries with parameterization
- **CORS Configuration**: Controlled cross-origin access
- **Token Expiration**: Automatic session management

## 🚀 Deployment

### Backend (Hugging Face Spaces)
The backend is configured for deployment on Hugging Face Spaces with Docker:

```dockerfile
FROM python:3.11-slim
# PostgreSQL support with psycopg2-binary
# Alembic migrations on startup
# Production-ready configuration
```

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `FRONTEND_URL`: CORS configuration for frontend

### Frontend (Vercel)
The frontend is optimized for Vercel deployment with Next.js:

```javascript
// next.config.js
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend API endpoint

### Database Setup
The system supports PostgreSQL for production deployment:

1. **Create PostgreSQL Database**: Set up managed PostgreSQL instance
2. **Configure Connection**: Set `DATABASE_URL` environment variable
3. **Run Migrations**: Alembic automatically runs migrations on startup
4. **Initialize Data**: Demo organization and users created automatically

## 📈 Monitoring & Analytics

### Dashboard Metrics
- **User Activity**: Login tracking and engagement metrics
- **Feedback Analytics**: Sentiment distribution and trends
- **Organization Health**: User adoption and system usage
- **Performance Tracking**: Response times and system health

### Reporting Features
- **Feedback History**: Complete audit trail of all feedback
- **User Management**: Invitation status and user lifecycle
- **Sentiment Analysis**: Automated sentiment tracking and reporting
- **Export Capabilities**: Data export for external analysis

## 🔄 Migration from Single-Tenant

For existing single-tenant deployments, the system provides:

1. **Backward Compatibility**: Existing APIs continue to work
2. **Data Migration**: Alembic migrations handle schema updates
3. **Default Organization**: Single-tenant data moved to default organization
4. **Role Mapping**: Existing roles mapped to new role system

## 🛠️ Development

### Local Development Setup

1. **Backend Setup**:
   ```bash
   cd project/backend
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd project/frontend
   npm install
   npm run dev
   ```

3. **Database Setup**:
   ```bash
   # PostgreSQL (recommended)
   createdb feedback_system
   export DATABASE_URL="postgresql://user:password@localhost/feedback_system"
   ```

### Testing
The system includes comprehensive test coverage:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and authorization testing
- **Performance Tests**: Load testing and optimization

## 📚 API Documentation

Interactive API documentation is available at `/docs` when running the backend server. The documentation includes:

- **Complete Endpoint Reference**: All available API endpoints
- **Request/Response Schemas**: Detailed data models
- **Authentication Examples**: How to authenticate requests
- **Error Handling**: Common error responses and handling

## 🤝 Contributing

We welcome contributions to improve the system:

1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: Work on specific features
3. **Write Tests**: Ensure comprehensive test coverage
4. **Submit Pull Request**: Detailed description of changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the comprehensive README and API docs
- **Issues**: Create GitHub issues for bugs and feature requests
- **Community**: Join discussions and share feedback

---

Built with ❤️ for modern HR teams and organizations seeking effective feedback management.