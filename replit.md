# Overview

This is a Telegram bot designed for movie channel management with integrated movie search capabilities and copyright protection features. The bot serves as a comprehensive solution for managing movie-related Telegram channels, providing users with movie search functionality, download links, and automated content moderation. It's built specifically for the MRapr Guild community and includes admin controls for channel management and content filtering.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework Architecture
- **Core Framework**: Python Telegram Bot (python-telegram-bot) library for handling Telegram API interactions
- **Modular Design**: Separated into distinct modules for handlers, admin functions, channel management, copyright filtering, and utilities
- **Asynchronous Processing**: Built with async/await patterns for handling concurrent operations

## Data Storage Strategy
- **File-based JSON Storage**: Uses local JSON files for persistent data storage instead of a traditional database
- **Data Directory Structure**: Centralized data management in `/data` directory with separate files for different data types
- **Configuration Management**: Environment variables for sensitive data (API keys, bot tokens) with fallback defaults

## Authentication and Authorization
- **Admin System**: Role-based access control with JSON-stored admin IDs
- **Permission Checking**: Decorator-based admin verification for restricted operations
- **Super Admin Concept**: Hierarchical admin system with a primary administrator

## Content Management and Filtering
- **Copyright Protection**: Keyword-based filtering system to detect and prevent copyright violations
- **Channel Management**: Multi-channel support with add/remove functionality for managed channels
- **Message Filtering**: Real-time content scanning with configurable keyword lists
- **Auto-moderation**: Automatic deletion of messages containing flagged content

## Movie Search Integration
- **Mock Database**: Currently uses in-memory movie database for demonstration
- **Search Functionality**: Text-based movie search with title, year, and quality information
- **Download Links**: Integration with external download sources through URL shortening

## URL Management
- **Custom URL Shortener**: Integration with mraprguilds.site for link shortening
- **API-based Shortening**: RESTful API integration with authentication headers
- **Fallback Handling**: Graceful degradation when shortening service is unavailable

# External Dependencies

## Telegram Bot API
- **python-telegram-bot**: Primary framework for Telegram bot functionality
- **Webhook/Polling**: Bot communication with Telegram servers
- **Inline Keyboards**: Interactive button interfaces for user interaction

## HTTP Client Libraries
- **aiohttp**: Asynchronous HTTP client for external API calls
- **URL Shortening Service**: Custom integration with mraprguilds.site API

## File System Dependencies
- **JSON File Storage**: Local file system for data persistence
- **Log File Management**: Rotating log files for debugging and monitoring
- **Configuration Files**: Environment-based configuration management

## External Channels and Services
- **Movie Search Channel**: https://t.me/mraprmoviesrequest for movie requests
- **Download Channel**: https://t.me/mraprguildofficialmovies for movie downloads
- **Website Integration**: https://www.mraprguilds.site for web presence
- **GitHub Repository**: https://github.com/Mraprguild for code hosting

## Environment Variables
- **BOT_TOKEN**: Telegram bot authentication token from BotFather
- **SHORTENER_API_KEY**: API key for URL shortening service
- **SUPER_ADMIN_ID**: Primary administrator user ID
- **BOT_USERNAME**: Bot's Telegram username for mentions

## Python Standard Library
- **logging**: Comprehensive logging system with file and console output
- **json**: Data serialization and storage
- **os**: Environment variable access and file system operations
- **re**: Regular expression pattern matching for validation
- **datetime**: Timestamp management and date operations