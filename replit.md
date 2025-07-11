# WeChat AI Publisher System

## Overview

This is a Flask-based web application that integrates with WeChat Official Account API and Google's Gemini AI service to automate content creation and publishing for WeChat public accounts. The system provides a web interface for configuration management, content generation using AI, and publishing articles to WeChat Official Accounts.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Interface**: Bootstrap 5-based responsive web UI with custom CSS styling
- **Template Engine**: Flask's Jinja2 templating system for server-side rendering
- **Client-side Features**: Real-time clock display, form handling, and interactive elements

### Backend Architecture
- **Framework**: Flask web framework with WSGI application structure
- **Application Structure**: Modular design with separate service classes for different integrations
- **Middleware**: ProxyFix for handling proxy headers in deployment environments
- **Logging**: Comprehensive logging system with file and console output

### Service Layer Components
1. **ConfigManager**: Handles configuration persistence and management
2. **WeChatAPI**: Encapsulates WeChat Official Account API interactions
3. **GeminiService**: Manages Google Gemini AI integration for content generation

## Key Components

### Configuration Management
- **File-based Storage**: JSON configuration files for persistent settings
- **Default Configuration**: Fallback configuration with sensible defaults
- **Dynamic Updates**: Runtime configuration updates with validation
- **Environment Integration**: Support for environment variables

### WeChat Integration
- **Access Token Management**: Automatic token acquisition and refresh handling
- **Draft Management**: Creating and managing article drafts
- **Publishing Pipeline**: Automated publishing from drafts to live articles
- **Material Upload**: Support for image and media uploads

### AI Content Generation
- **Gemini AI Integration**: Google's Gemini 2.5 Flash model for content generation
- **Prompt Processing**: Structured prompt handling for consistent content generation
- **Error Handling**: Robust error handling for API failures and rate limits

### Web Interface
- **Responsive Design**: Mobile-friendly Bootstrap-based UI
- **Real-time Updates**: Dynamic content updates without page refresh
- **Form Validation**: Client and server-side validation for configuration inputs
- **Status Monitoring**: Real-time display of system status and operations

## Data Flow

1. **Configuration Setup**: Users input WeChat credentials and Gemini API keys through web interface
2. **Token Management**: System automatically manages WeChat access tokens with expiration handling
3. **Content Generation**: AI generates content based on user prompts and system templates
4. **Draft Creation**: Generated content is formatted and saved as WeChat drafts
5. **Publishing**: Drafts are submitted for publication through WeChat API
6. **Status Tracking**: System monitors and logs all operations for debugging and analytics

## External Dependencies

### WeChat Official Account API
- **Authentication**: AppID and AppSecret-based authentication
- **Rate Limiting**: Handles API quotas and frequency limits
- **Content Management**: Draft creation, material upload, and publishing

### Google Gemini AI
- **API Integration**: RESTful API integration with proper authentication
- **Model Selection**: Configurable model selection (default: gemini-2.5-flash)
- **Content Generation**: Text generation with prompt-based inputs

### Third-party Libraries
- **Flask**: Web framework and routing
- **Requests**: HTTP client for external API calls
- **Google GenAI**: Official Google Generative AI client library
- **Bootstrap**: Frontend UI framework

## Deployment Strategy

### Environment Setup
- **Python Requirements**: Flask-based application requiring Python 3.7+
- **Environment Variables**: Support for production configuration through environment variables
- **File System**: Requires write access for logs, cache, and configuration files

### Directory Structure
- **logs/**: Application logs with date-based rotation
- **cache/**: Temporary file storage for processing
- **templates/**: HTML templates for web interface
- **static/**: CSS, JavaScript, and other static assets
- **attached_assets/**: Example scripts and configuration files

### Production Considerations
- **WSGI Deployment**: Ready for deployment with Gunicorn or uWSGI
- **Proxy Support**: Built-in proxy handling for reverse proxy deployments
- **Security**: Session management with configurable secret keys
- **Monitoring**: Comprehensive logging for production monitoring

### Scalability Features
- **Stateless Design**: Session-based state management for horizontal scaling
- **External Configuration**: Environment-based configuration for multiple deployments
- **Error Recovery**: Robust error handling and recovery mechanisms
- **API Rate Limiting**: Built-in handling of external API limitations