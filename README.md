# DataAssist 🤖📊

DataAssist is an AI-powered Django web application that helps users generate SQL and NoSQL queries through natural language processing and provides intelligent data visualization capabilities. It supports multiple database types and file formats, making data analysis accessible to users of all technical levels.

## ✨ Features

### 🔗 Database Connectivity
- **Multi-Database Support**: Connect to various database types including:
  - MySQL
  - PostgreSQL
  - SQLite
  - MongoDB
  - And more...

### 📁 File Upload Support
- Upload and analyze data from multiple file formats:
  - Excel (.xlsx, .xls)
  - CSV files
  - JSON files
  - And other common data formats

### 🧠 AI-Powered Query Generation
- **Natural Language to SQL**: Convert plain English questions into executable SQL queries
- **NoSQL Support**: Generate MongoDB queries with proper syntax
- **Google Gemini Integration**: Powered by Google's Gemini AI for accurate query generation
- **Query Optimization**: AI-optimized queries following best practices

### 📊 Data Visualization
- Interactive charts and graphs
- Multiple visualization types
- Matplotlib and Seaborn integration
- Export visualization capabilities

### 📝 Query History
- Track all your queries and results
- Timestamp-based history
- User-specific query management
- Easy access to previous analyses

### 👤 User Management
- User registration and authentication
- Secure login system
- Personal query history
- Session management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.1+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DataAssist
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Gemini API**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Update the API key in `main/genai.py`
   - **⚠️ Security Note**: Never commit API keys to version control

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser to `http://localhost:8000`

## 🐳 Docker Deployment

### Quick Start with Docker Compose
```bash
# Build and run
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f web
```

### Manual Docker Build
```bash
# Build image
docker build -t dataassist .

# Run container
docker run -d -p 8000:8000 --name dataassist-app dataassist
```

For detailed Docker deployment instructions, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md).

## 💻 Usage

### 1. User Registration
- Create a new account through the signup page
- Login with your credentials

### 2. Database Connection
- **Direct Database Connection**: Enter connection parameters for your database
- **File Upload**: Upload Excel, CSV, or JSON files for analysis
- **URL Connection**: Connect to remote databases via URL

### 3. Query Generation
- Navigate to the Query Helper
- Ask questions in plain English like:
  - "Show me all users with age greater than 30"
  - "Find the top 10 products by sales"
  - "Calculate average revenue by month"

### 4. Data Visualization
- Generate charts and graphs from your query results
- Multiple visualization types available
- Interactive and exportable visualizations

### 5. History Management
- View all your previous queries
- Re-run historical queries
- Track analysis patterns over time

## 🏗️ Project Structure

```
DataAssist/
├── dataassist/              # Django project configuration
│   ├── settings.py          # Development settings
│   ├── settings_prod.py     # Production settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── main/                   # Main application
│   ├── Database_mangers/   # Database connection managers
│   ├── views/              # View controllers
│   │   ├── connection.py   # Database connection handling
│   │   ├── queryhelper.py  # AI query generation
│   │   ├── visualization.py # Data visualization
│   │   └── history.py      # Query history management
│   ├── models.py           # Database models
│   ├── genai.py           # Google Gemini AI integration
│   ├── pandas_tool.py     # Pandas data processing
│   └── tools.py           # Utility functions
├── templates/              # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker compose configuration
├── Dockerfile            # Docker build instructions
└── manage.py             # Django management script
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
DATABASE_URL=your-database-url
GEMINI_API_KEY=your-gemini-api-key
```

### Database Configuration
Update `DATABASES` in `settings.py` for your preferred database:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🤖 AI Integration Details

### Google Gemini Configuration
The application uses Google Gemini 2.0 Flash for query generation with:
- **Temperature**: 0.2 (for precise, deterministic outputs)
- **Max Output Tokens**: 8192
- **Specialized System Instructions**: Optimized for SQL/NoSQL query generation

### Query Generation Process
1. User inputs natural language question
2. AI analyzes question context and database metadata
3. Generates optimized SQL/NoSQL query
4. Returns executable query with proper syntax
5. Stores query and results in user history

## 📊 Supported Database Types

| Database | Query Type | Status |
|----------|------------|--------|
| MySQL | SQL | ✅ Supported |
| PostgreSQL | SQL | ✅ Supported |
| SQLite | SQL | ✅ Supported |
| MongoDB | NoSQL | ✅ Supported |
| File Uploads | Pandas | ✅ Supported |

## 📈 Visualization Features

- **Chart Types**: Bar, Line, Pie, Scatter, Histogram, Heatmap
- **Libraries**: Matplotlib, Seaborn integration
- **Export**: PNG, PDF, SVG formats
- **Interactive**: Dynamic chart generation based on query results

## 🔐 Security Features

- **CSRF Protection**: Django built-in CSRF protection
- **SQL Injection Prevention**: Parameterized queries
- **User Authentication**: Secure login system
- **API Key Security**: Environment-based API key management
- **Input Validation**: Query sanitization and validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python manage.py test

# Run with debug mode
python manage.py runserver --debug
```

## 🐛 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

2. **Database Connection Errors**
   - Verify database credentials
   - Check database server connectivity
   - Ensure database exists

3. **Gemini API Errors**
   - Verify API key is correct
   - Check API quotas and limits
   - Ensure internet connectivity

4. **File Upload Issues**
   - Check file permissions in `media/` directory
   - Verify file format compatibility
   - Check maximum file size limits

### Debug Mode
Enable debug mode by setting `DEBUG = True` in settings.py for detailed error messages.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Development Team** - Initial work and ongoing development

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- Django framework for robust web development
- Bootstrap for responsive UI components
- Chart.js and visualization libraries

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the Docker deployment guide for deployment issues

## 🔄 Version History

- **v1.0.0** - Initial release with core features
  - AI-powered query generation
  - Multi-database support
  - Data visualization
  - User management
  - Docker deployment support

---

**DataAssist** - Making data analysis accessible through AI-powered natural language processing! 🚀