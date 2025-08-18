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

This project is designed for free deployment with the frontend on Vercel and the backend on Hugging Face Spaces.

### Environment Variables

**Frontend (Vercel):**
Set the `VITE_API_URL` environment variable in your Vercel project settings to point to your deployed Hugging Face Spaces backend URL.

**Backend (Hugging Face Spaces):**
Set the `FRONTEND_URL` environment variable in your Hugging Face Spaces project settings to your deployed Vercel frontend URL for CORS configuration.

### Frontend Deployment (Vercel)

1.  **Push to GitHub**: Ensure your `project/frontend` directory is pushed to a GitHub repository.
2.  **Connect to Vercel**:
    *   Go to Vercel and import your Git repository.
    *   When configuring the project, select the `frontend` directory as the root directory.
    *   Vercel will automatically detect it as a Vite project and set the build command (`npm run build`) and output directory (`dist`).
    *   Add the `VITE_API_URL` environment variable in the Vercel dashboard, pointing to your Hugging Face Spaces backend URL (e.g., `https://YOUR-SPACE-NAME.hf.space/api`).
3.  **Deploy**: Vercel will build and deploy your frontend.

### Backend Deployment (Hugging Face Spaces)

1.  **Push to GitHub**: Ensure your `project/backend` directory is pushed to a GitHub repository.
2.  **Create a New Space**:
    *   Go to Hugging Face Spaces and create a new Space.
    *   Choose "Docker" as the Space SDK.
    *   Connect your Git repository.
    *   Ensure the `backend` directory is the root of your Space repository.
3.  **Configure Environment Variables**:
    *   In your Hugging Face Space settings, add the `FRONTEND_URL` environment variable, pointing to your Vercel frontend URL (e.g., `https://your-vercel-app.vercel.app`).
4.  **Deployment**: Hugging Face Spaces will automatically build and deploy your FastAPI application using the provided `Dockerfile` (or `requirements.txt` and `app.py` if you choose that route). The `/health` endpoint can be used to verify deployment.

### Post-Deployment Integration

Once both the frontend and backend are deployed:

1.  **Update Frontend API URL**: If you haven't already, ensure the `VITE_API_URL` in your Vercel environment variables is set to the public URL of your Hugging Face Spaces backend (e.g., `https://YOUR-SPACE-NAME.hf.space/api`).
2.  **Update Backend CORS**: Ensure the `FRONTEND_URL` in your Hugging Face Spaces environment variables is set to the public URL of your Vercel frontend (e.g., `https://your-vercel-app.vercel.app`).
3.  **Test**: Access your Vercel frontend URL and test the full application workflow (login, feedback submission, etc.) to ensure seamless communication with the backend.

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
