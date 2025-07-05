# API Configuration
API_HOST="0.0.0.0"
API_PORT=8000
DEBUG=True

# Frontend Configuration
FRONTEND_URL="http://localhost:3000"

# Gemini AI Configuration
GEMINI_API_KEY="your_gemini_api_key"

# DataStax Configuration
DATASTAX_CLIENT_ID="your_datastax_client_id"
DATASTAX_CLIENT_SECRET="your_datastax_client_secret"



# Social Media Analytics Platform

A comprehensive analytics platform that helps you understand and optimize your social media content performance using FastAPI, Google's Gemini AI, and DataStax Astra DB.

## Project Structure

```
SocialMediaAnalysis/
├── backend/                    # Backend FastAPI application
│   ├── __pycache__/           # Python cache files
│   ├── main.py               # FastAPI application entry point
│   ├── datastax_service.py   # DataStax Astra DB service
│   ├── db_config.py         # Database configuration
│   ├── .env                 # Environment variables
│   └── secure-connect-social-media-analytics.zip  # DataStax secure connect bundle
├── frontend/                  # Frontend React application
│   ├── public/               # Static assets and entry point
│   │   ├── favicon.ico      # Application icon
│   │   ├── index.html      # HTML template
│   │   └── manifest.json   # PWA manifest
│   └── src/                 # React source code
│       ├── App.js          # Main application component
│       └── index.js        # Application entry point
├── requirements.txt          # Python dependencies
├── .gitignore              # Git ignore file
└── README.md              # Project documentation
```

## Frontend File Details

### Public Directory
- `favicon.ico`: Application icon displayed in browser tab
- `index.html`: Main HTML template that loads the React application
- `manifest.json`: Web App Manifest for PWA features

### Source Directory
- `App.js`: Main React component containing the application structure
- `index.js`: Entry point that renders the React application

### Package.json
Contains project dependencies and scripts for:
- Development server
- Build process
- Testing
- Linting

### Important Notes
1. **Build Files**
   - Frontend build files are automatically generated and should not be committed
   - These include: `build/`, `.next/`, `dist/` directories

2. **Dependencies**
   - Use `npm install` to install dependencies from package.json
   - Never commit the `node_modules` directory

3. **Environment Variables**
   - Frontend environment variables should be managed through `.env` files
   - Create a `.env.example` file for frontend configuration

## Important Files to Skip in GitHub

1. **Environment Variables**
   - `.env` - Contains sensitive API keys and configuration
   - Create a `.env.example` file with placeholder values instead

2. **Database Connection Files**
   - `secure-connect-social-media-analytics.zip` - Contains database credentials
   - Share this file securely with team members

3. **Generated Files**
   - `__pycache__` - Python cache files
   - `venv313` - Virtual environment
   - `.dist` - Distribution files

4. **Frontend Build Files**
   - `frontend/node_modules`
   - `frontend/.next`
   - `frontend/build`

## Git Setup

1. Create a `.gitignore` file with the following content:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv313/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment Variables
.env

# Distribution
.dist/

# DataStax Secure Connect Bundle
secure-connect-social-media-analytics.zip

# Frontend
frontend/node_modules/
frontend/.next/
frontend/build/
frontend/dist/

# Logs
*.log
logs/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

2. Create a `.env.example` file:

```env
# API Configuration
API_HOST="0.0.0.0"
API_PORT=8000
DEBUG=True

# Frontend Configuration
FRONTEND_URL="http://localhost:3000"

# Gemini AI Configuration
GEMINI_API_KEY="your_gemini_api_key"

# DataStax Configuration
DATASTAX_CLIENT_ID="your_datastax_client_id"
DATASTAX_CLIENT_SECRET="your_datastax_client_secret"
```

## GitHub Setup Steps

1. Initialize git repository:
```bash
git init
```

2. Add all files:
```bash
git add .
```

3. Commit:
```bash
git commit -m "Initial commit"
```

4. Create a GitHub repository
5. Push to GitHub:
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

## Security Best Practices

1. Never commit `.env` file with real credentials
2. Always use `.env.example` for reference
3. Keep sensitive files like `secure-connect-social-media-analytics.zip` secure
4. Use environment-specific configuration files
5. Regularly rotate API keys and credentials

## Project Structure

```
SocialMediaAnalysis/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes and endpoints
│   │   ├── models/        # Database models and schemas
│   │   ├── services/      # Business logic and services
│   │   └── utils/         # Utility functions and helpers
│   ├── config/           # Configuration files
│   ├── tests/            # Unit and integration tests
│   ├── main.py          # FastAPI application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── public/          # Static assets
│   ├── src/             # React components and pages
│   └── package.json     # Frontend dependencies
├── .dist/              # Distribution files
└── README.md          # Project documentation
```

## Features

- **Post Analytics**: Track likes, shares, and comments for different post types (carousel, reel, static)
- **AI-Powered Insights**: Get intelligent analysis of your content performance using Google's Gemini AI
- **Time-based Analytics**: Understand the best posting times for maximum engagement
- **Trending Hashtags**: Track popular hashtags to optimize your content strategy
- **Performance Comparison**: Compare different post types to identify what works best
- **Real-time Insights**: Get instant feedback on your social media strategy
- **Database Integration**: Uses DataStax Astra DB for scalable data storage
- **API Documentation**: Comprehensive Swagger/OpenAPI documentation

## Database Setup

### Current Database (DataStax Astra DB)

- **Why DataStax Astra DB?**
  - Scalable NoSQL database
  - Built-in analytics capabilities
  - High availability and performance
  - Easy integration with FastAPI
  - Cost-effective for social media analytics

- **Database Schema**
  ```sql
  CREATE TABLE posts (
      id UUID PRIMARY KEY,
      post_type TEXT,
      likes INT,
      shares INT,
      comments INT,
      created_at TIMESTAMP,
      hashtags SET<TEXT>
  );
  
  CREATE TABLE analytics (
      post_type TEXT,
      average_likes DECIMAL,
      average_shares DECIMAL,
      average_comments DECIMAL,
      engagement_rate DECIMAL,
      PRIMARY KEY (post_type)
  );
  ```

### Changing Database

To switch to a different database:

1. Update `backend/app/config/database.py`:
   - Replace DataStax Astra DB configuration with your preferred database
   - Update connection parameters and drivers

2. Modify database models in `backend/app/models/`:
   - Update schema definitions
   - Adjust ORM mappings

3. Update environment variables:
   - Remove DataStax specific variables
   - Add new database configuration variables

## Prerequisites

- Python 3.13+
- Node.js (for frontend)
- FastAPI
- Pandas
- Google Gemini AI API key
- DataStax Astra DB account

## Installation Steps

1. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv313
   .\venv313\Scripts\activate  # Windows
   source venv313/bin/activate  # Linux/Mac
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Create .env file in backend directory
   cp backend/.env.example backend/.env
   
   # Edit backend/.env with your configurations
   ```

2. **Frontend Setup**
   ```bash
   # Navigate to frontend directory
   cd frontend
   
   # Install Node dependencies
   npm install
   
   # Start development server
   npm start
   ```

3. **Database Setup**
   ```bash
   # Create database tables
   python -m backend.app.utils.database_setup
   
   # Initialize database with sample data
   python -m backend.app.utils.seed_data
   ```

4. **API Documentation**
   - Access Swagger UI at http://localhost:8000/docs
   - Access ReDoc at http://localhost:8000/redoc

## API Endpoints

### Post Management
- `GET /api/posts`: List all posts
- `POST /api/posts`: Create a new post
- `GET /api/posts/{post_id}`: Get specific post details
- `DELETE /api/posts/{post_id}`: Delete a post

### Analytics
- `GET /api/analytics/{post_type}`: Get analytics for specific post type
- `GET /api/analytics/engagement`: Get overall engagement metrics
- `GET /api/analytics/time-based`: Get time-based analytics
- `GET /api/analytics/hashtags`: Get trending hashtags

### AI Analysis
- `GET /api/ai/performance-analysis`: Get AI-powered performance analysis
- `GET /api/ai/content-recommendations`: Get content strategy recommendations
- `GET /api/ai/engagement-patterns`: Get engagement pattern analysis

## Gemini AI Integration

The platform uses Google's Gemini AI to provide:
1. Performance comparison between different post types
2. Content strategy recommendations
3. Key insights about engagement patterns
4. Suggestions for improvement

To use the AI features:
1. Get your API key from https://makersuite.google.com/app/apikey
2. Add it to your `.env` file
3. Test the `/api/ai/performance-analysis` endpoint

## Sample Response

```json
{
  "analytics": {
    "carousel": {
      "average_likes": 175.0,
      "average_shares": 52.5,
      "average_comments": 35.0
    },
    "reel": {
      "average_likes": 475.0,
      "average_shares": 135.0,
      "average_comments": 75.0
    },
    "static": {
      "average_likes": 110.0,
      "average_shares": 22.5,
      "average_comments": 16.5
    }
  },
  "engagement_rates": {
    "carousel": 87.5,
    "reel": 228.33,
    "static": 49.67
  },
  "ai_analysis": {
    "performance_comparison": "Detailed analysis of performance metrics",
    "recommendations": [
      "Use more carousel posts during peak engagement hours",
      "Optimize static posts with trending hashtags"
    ],
    "engagement_patterns": "Detailed patterns and insights"
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Interview Preparation Questions

### Technical Questions

1. **Database Design**
   - Why did you choose DataStax Astra DB?
   - How does your database schema support analytics queries?
   - What optimizations did you implement for performance?

2. **API Design**
   - Explain your API endpoint design
   - How did you handle rate limiting?
   - Describe your error handling strategy

3. **AI Integration**
   - How does Gemini AI integrate with your platform?
   - What kind of preprocessing do you perform on data?
   - How do you handle AI model responses?

4. **Scalability**
   - How would you scale this application?
   - What caching strategies did you implement?
   - How do you handle large datasets?

5. **Security**
   - Describe your authentication flow
   - How do you protect sensitive data?
   - What security measures are in place for API access?

### Behavioral Questions

1. **Problem Solving**
   - Describe a challenging problem you faced during development
   - How did you handle unexpected API responses?
   - What was your approach to debugging performance issues?

2. **Team Collaboration**
   - How did you work with frontend developers?
   - Describe your experience with code reviews
   - How did you handle conflicting requirements?

3. **Learning and Growth**
   - What new technologies did you learn during this project?
   - How did you stay updated with API changes?
   - What improvements would you make to the current implementation?

## Best Practices

1. **Code Organization**
   - Follow RESTful API design principles
   - Implement proper error handling
   - Use meaningful variable and function names

2. **Performance Optimization**
   - Implement caching where appropriate
   - Optimize database queries
   - Use async/await for I/O operations

3. **Testing**
   - Write unit tests for API endpoints
   - Implement integration tests
   - Use test-driven development approach

4. **Documentation**
   - Maintain clear API documentation
   - Document database schema changes
   - Keep README updated with setup instructions

## Future Enhancements

1. **Advanced Analytics**
   - Implement more sophisticated AI models
   - Add predictive analytics capabilities
   - Enhance real-time processing

2. **User Interface**
   - Add more interactive visualizations
   - Implement dark mode
   - Add export functionality

3. **Performance**
   - Implement caching layers
   - Optimize database queries
   - Add load balancing

4. **Security**
   - Add two-factor authentication
   - Implement API rate limiting
   - Add more robust validation

## Running the Application

1. Start the backend server:
```bash
cd backend
python -m uvicorn main:app --reload
```

2. Access the API documentation:
   - Open http://localhost:8000/docs in your browser
   - Test the available endpoints

## API Endpoints

- `GET /posts`: List all posts
- `GET /analytics/{post_type}`: Get analytics for a specific post type
- `GET /performance-analysis`: Get AI-powered analysis of post performance
- `GET /insights/{post_type}`: Get insights for a specific post type
- `GET /time-analytics`: Get time-based analytics
- `GET /trending-hashtags`: Get trending hashtags
- `POST /posts`: Create a new post

## Gemini AI Integration

The platform uses Google's Gemini AI to provide:
1. Performance comparison between different post types
2. Content strategy recommendations
3. Key insights about engagement patterns
4. Suggestions for improvement

To use the AI features:
1. Get your API key from https://makersuite.google.com/app/apikey
2. Add it to your `.env` file
3. Test the `/performance-analysis` endpoint

## Sample Response

```json
{
  "analytics": {
    "carousel": {
      "average_likes": 175.0,
      "average_shares": 52.5,
      "average_comments": 35.0
    },
    "reel": {
      "average_likes": 475.0,
      "average_shares": 135.0,
      "average_comments": 75.0
    },
    "static": {
      "average_likes": 110.0,
      "average_shares": 22.5,
      "average_comments": 16.5
    }
  },
  "engagement_rates": {
    "carousel": 87.5,
    "reel": 228.33,
    "static": 49.67
  },
  "ai_analysis": "Detailed AI analysis of performance and recommendations"
}
```

## Contributing

Feel free to open issues and pull requests for any improvements you'd like to add.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
