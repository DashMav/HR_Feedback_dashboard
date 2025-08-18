# Lightweight Feedback System

A modern, secure feedback management system for internal team communication between managers and employees.

## Features

### Core Features (MVP)
- **Authentication & Roles**: Secure login system with Manager and Employee roles
- **Feedback Submission**: Structured feedback with strengths, improvements, and sentiment
- **Feedback Visibility**: Role-based access control with proper permissions
- **Dashboard**: Comprehensive overview for both managers and employees
- **Feedback History**: Complete timeline of all feedback interactions

### Bonus Features Implemented
- **Markdown Support**: Rich text formatting for feedback and comments
- **Tags System**: Categorize feedback with custom tags
- **Employee Comments**: Two-way communication on feedback
- **Acknowledgment System**: Track when feedback has been read
- **Responsive Design**: Works perfectly on all devices
- **Real-time Updates**: Instant feedback on all actions

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **React Markdown** for rich text rendering
- **Lucide React** for icons
- **Date-fns** for date formatting

### Backend
- **Python** with FastAPI
- **SQLAlchemy** ORM with SQLite database
- **JWT** authentication
- **Bcrypt** password hashing
- **Pydantic** for data validation
- **CORS** middleware for cross-origin requests

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker (optional)

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

#### Option 1: Local Python Environment
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

#### Option 2: Docker
```bash
# Navigate to backend directory
cd backend

# Build Docker image
docker build -t feedback-system-backend .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data feedback-system-backend
```

The backend API will be available at `http://localhost:8000`

### Demo Accounts

The system comes with pre-configured demo accounts:

**Manager Account:**
- Email: `manager@company.com`
- Password: `password123`

**Employee Account:**
- Email: `employee@company.com`
- Password: `password123`

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Get current user info
- `GET /api/employees` - Get team members (managers only)
- `POST /api/feedback` - Create new feedback
- `GET /api/feedback/received` - Get received feedback (employees)
- `POST /api/feedback/{id}/acknowledge` - Acknowledge feedback
- `POST /api/feedback/{id}/comment` - Add comment to feedback

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `name` - Full name
- `password_hash` - Bcrypt hashed password
- `role` - 'manager' or 'employee'
- `manager_id` - Foreign key to manager (for employees)

### Feedback Table
- `id` - Primary key
- `employee_id` - Foreign key to employee
- `manager_id` - Foreign key to manager
- `strengths` - Positive feedback text
- `improvements` - Areas for improvement
- `sentiment` - 'positive', 'neutral', or 'negative'
- `tags` - JSON array of tags
- `acknowledged` - Boolean acknowledgment status
- `employee_comment` - Optional employee response
- `created_at` - Creation timestamp
- `updated_at` - Last modification timestamp

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt with salt for password security
- **Role-Based Access Control**: Strict permissions based on user roles
- **Data Isolation**: Users can only access their own data
- **CORS Protection**: Configured for specific origins
- **Input Validation**: Comprehensive validation using Pydantic

## Architecture Highlights

### Frontend Architecture
- **Component-based**: Modular React components with clear separation of concerns
- **Context API**: Centralized authentication state management
- **Custom Hooks**: Reusable logic for API interactions
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation

### Backend Architecture
- **RESTful API**: Clean, predictable API design
- **ORM Integration**: SQLAlchemy for database operations
- **Dependency Injection**: FastAPI's dependency system for clean code
- **Error Handling**: Comprehensive error responses
- **Data Validation**: Automatic request/response validation

## Deployment

### Frontend Deployment
The frontend can be deployed to any static hosting service:

```bash
npm run build
# Deploy the 'dist' folder to your hosting service
```

### Backend Deployment
The backend includes a Dockerfile for easy deployment:

```bash
# Build and run with Docker
docker build -t feedback-system .
docker run -p 8000:8000 feedback-system
```

For production, consider:
- Using PostgreSQL instead of SQLite
- Setting up proper environment variables
- Implementing proper logging
- Adding rate limiting
- Setting up HTTPS

## Future Enhancements

- Email notifications for new feedback
- Anonymous peer feedback
- PDF export functionality
- Advanced analytics and reporting
- Integration with HR systems
- Mobile app development
- Real-time notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.