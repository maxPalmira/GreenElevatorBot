<p align="center">
  <a href="https://t.me/example_store_bot"><img src="data/assets/logo.png" alt="ShopBot"></a>
</p>

# Green Elevator Wholesale Bot

A Telegram bot developed to manage cannabis wholesale operations, primarily targeting the market in Thailand. Built using the aiogram framework, this bot facilitates interactions between customers and administrators, offering a streamlined platform for browsing products, managing orders, and providing customer support.

## Deployment

⚠️ **IMPORTANT: Railway-Only Deployment**

This bot is designed to run **exclusively** on Railway platform. We do not support or maintain local deployment options.

Key points about our deployment strategy:
- ✅ All deployments must be done through Railway
- ❌ Local development server is not supported
- ✅ Webhook mode is required (no polling)
- ✅ Railway handles all infrastructure needs
- ✅ Environment variables are managed through Railway dashboard

To deploy:
1. Push to the main branch
2. Railway will automatically deploy
3. Verify webhook setup through Telegram's getWebhookInfo

For monitoring:
- Use Railway's built-in logs
- Check the /health endpoint on Railway
- Monitor through Telegram's bot API

## Monitoring and Health Checks

The repository includes a `check_railway_health.py` script for reliable monitoring:

```bash
# Run the health checker
./check_railway_health.py

# Run with a specific bot token
./check_railway_health.py --token YOUR_BOT_TOKEN
```

This script checks:
1. **Telegram Webhook Status** - verifies the webhook URL is set correctly, checks for errors
2. **Railway Health Endpoint** - confirms the Railway deployment is running properly

Use this tool whenever you need to verify your bot's status or troubleshoot deployment issues. It's much more reliable than trying to parse Railway logs directly.

## Recent Updates

*   🧹 Code cleanup and removal of unused modules
*   🔄 Improved logging system with consistent timestamps
*   🎯 Enhanced error handling and state management
*   🌟 Cleaner code structure and organization
*   📝 Better documentation and code comments

## Features

### User Features
*   🌿 Product Catalog: Browse products organized by categories (Premium Strains, Hybrid Strains, Bulk Deals)
*   🛒 Shopping Cart: Add products, adjust quantities, and remove items before checkout
*   📦 Order Management: Place orders and track delivery status
*   👥 Order Tracking: View the status of active orders
*   💬 Customer Support: Submit questions to administrators (limited to 3 pending questions)

### Admin Features
*   📦 Product Management: Add, edit, or delete products with details
*   📋 Order Management: View and manage customer orders
*   ❓ Customer Questions: Access and respond to inquiries
*   🔒 Category Management: Add or delete product categories
*   📊 Detailed Analytics: Monitor bot activity and user interactions

### System Features
*   🔐 Role-based Access Control
*   📝 Comprehensive Logging
*   🔄 Process Management
*   🛡️ Security Features

## Quick Start

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd GreenElevetorTelegramBot_test
    ```
2.  Create a virtual environment:
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate  # Unix/macOS
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables in `.env` file (see Configuration section below)

### Bot Management

The bot can be managed using the `manage_bot.py` script:

```bash
# Start the bot
python manage_bot.py start

# Stop the bot
python manage_bot.py stop

# Restart the bot
python manage_bot.py restart

# Check bot status
python manage_bot.py status
```

### Basic Usage

#### User Features

1.  Start the bot in Telegram using the `/start` command
2.  Browse products via "🌿 Products"
3.  Add items to your cart
4.  View your cart and manage quantities
5.  Proceed to checkout
6.  Track your orders
7.  Contact support with "☎️ Contact"

#### Admin Features

1.  Access admin panel with proper permissions
2.  Manage products (add, edit, delete)
3.  View and manage orders
4.  Update order statuses
5.  Respond to customer inquiries

## Technical Details

### Database Support

The bot uses **PostgreSQL** for production deployment:

- Robust relational database with excellent concurrency support
- Native integration with Railway platform
- Reliable performance for production use
- Good scaling capabilities

#### Setting Up PostgreSQL on Railway

To set up PostgreSQL on Railway:

1. Provision a PostgreSQL database in Railway:
   - Go to your Railway project dashboard
   - Click "New" and select "Database" → "PostgreSQL"
   - Wait for the provisioning to complete

2. Set the DATABASE_URL environment variable:
   - Railway automatically sets DATABASE_URL for your application
   - Use this variable in your application to connect to the database

3. Verify your PostgreSQL connection:
   ```bash
   # Test the connection to PostgreSQL
   ./test_postgres.py
   ```

4. If needed, you can initialize or check the database:
   ```bash
   # Check database health and populate with sample data if needed
   ./check_railway_db.py
   ```

### Database Schema

The bot uses PostgreSQL with the following schema:

1. Users Table:
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

2. Categories Table:
```sql
CREATE TABLE categories (
    idx SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL
)
```

3. Products Table:
```sql
CREATE TABLE products (
    idx VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    image VARCHAR(1024),
    price INTEGER NOT NULL,
    tag INTEGER REFERENCES categories(idx)
)
```

4. Cart Table:
```sql
CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    product_id VARCHAR(255) REFERENCES products(idx),
    quantity INTEGER DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

5. Orders Table:
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    address TEXT,
    phone VARCHAR(50),
    total_price INTEGER
)
```

6. Order Items Table:
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id VARCHAR(255) REFERENCES products(idx),
    quantity INTEGER DEFAULT 1,
    price INTEGER NOT NULL
)
```

### Bot Architecture

The bot is built using:
- aiogram framework for Telegram Bot API
- PostgreSQL for database storage
- Asynchronous handlers for better performance
- Retry logic for API calls
- State management for multi-step operations

Key components:
1. `app.py`: Main bot application
2. `manage_bot.py`: Bot process management
3. `loader.py`: Bot initialization and configuration
4. `handlers/`: Message and callback handlers
5. `utils/`: Utility functions and database management
6. `keyboards/`: Telegram keyboard layouts
7. `states/`: FSM states for multi-step operations

## Configuration

Configure the bot using a `.env` file in the project root:

*   `BOT_TOKEN`: Your Telegram Bot API token
*   `ADMINS`: Comma-separated list of Telegram User IDs for admins
*   `DATABASE_URL`: PostgreSQL connection URL (provided by Railway)
*   `DATABASE_TYPE`: Set to "postgres" for PostgreSQL

Example `.env` file:
```
BOT_TOKEN=your_bot_token_here
ADMINS=123456789,987654321
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://postgres:password@hostname:port/railway
```

## Dependencies

*   `aiogram==2.25.1`: Telegram Bot API framework
*   `python-dotenv==1.0.0`: Environment variable management
*   `SQLAlchemy==2.0.23`: SQL toolkit and ORM
*   `aiohttp==3.8.6`: Asynchronous HTTP client/server
*   `Pillow==9.5.0`: Image processing
*   `python-dateutil==2.8.2`: DateTime utilities
*   `psycopg2-binary==2.9.9`: PostgreSQL adapter for Python
*   `requests==2.31.0`: HTTP library

## Error Handling

The bot implements:
- Retry logic for Telegram API calls
- Database transaction management
- Graceful process termination
- Logging for debugging and monitoring
- State cleanup on errors

## Security Features

1. Admin Authentication:
   - Admin commands protected by middleware
   - User ID verification
   - Environment-based configuration

2. Data Protection:
   - SQL injection prevention
   - Input validation
   - Secure process management

## Deployment Notes

1. Process Management:
   - Uses dedicated process management
   - PID file tracking
   - Graceful shutdown support
   - Status monitoring

2. Database:
   - Automatic table creation
   - Foreign key constraints
   - Unique constraints where needed
   - Transaction support

3. Monitoring:
   - Structured logging
   - Process status tracking
   - Database query logging
   - Error tracking

## Logging System

The bot implements a comprehensive logging system:

1. Log Types:
   - System events (startup/shutdown)
   - User interactions
   - Message updates
   - Error tracking
   - Heartbeat monitoring (5-second intervals)

2. Log Storage:
   - `logs/bot.log`: Main log (10MB, 5 backups)
   - `logs/heartbeat.log`: Heartbeat log (1MB, 2 backups)
   - Timestamp format: `YYYY-MM-DD HH:MM:SS`

3. Monitoring Features:
   - Real-time console output
   - Rotating file system
   - Activity status updates
   - Message count tracking
   - Uptime monitoring

## Menu

The user menu looks like this:

![User Menu](data/assets/4.png)

## Catalog

The catalog consists of products sorted by categories. Users can add items to their cart, and the admin has full control over catalog management (addition/removal).

## Cart

The ordering process looks like this: the user goes to the `🛍️ Catalog`, selects the desired category, chooses products, and clicks the `🛒 Cart` button.

![cart](data/assets/5.png)

---

Then, after making sure everything is in place, proceed to checkout by clicking `📦 Place Order`.

![checkout](data/assets/6.png)

## Add a Product

To add a product, select a category and click the `➕ Add Product` button. Then, fill out the "name-description-image-price" form and confirm.

![add_product](data/assets/1.png)

## Contacting Administration

To ask the admin a question, simply select the `/sos` command. There is a limit on the number of questions.

![sos](data/assets/7.png)

## Directory Structure

```
.
├── src/                    # Source code directory
│   ├── app.py             # Main bot application
│   ├── loader.py          # Bot initialization
│   ├── manage_bot.py      # Process management
│   ├── assets/            # Static assets and resources
│   ├── handlers/          # Message and callback handlers
│   ├── keyboards/         # Telegram keyboard layouts
│   ├── states/            # FSM states
│   ├── utils/            # Utility functions
│   └── filters/          # Custom filters
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── functional/       # Functional tests
│   ├── run_tests.py      # Test runner
│   ├── test_bot.py       # Bot tests
│   └── pytest.ini        # Pytest configuration
├── data/                 # Data storage
├── docs/                # Documentation
├── run/                 # Runtime files
│   └── bot.pid         # Process ID file
├── .env                # Environment variables
├── .env.test           # Test environment variables
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── LICENSE           # License information
└── .gitignore       # Git ignore rules
```

### Key Directories

- `src/`: Contains all source code files
  - `app.py`: Main application entry point
  - `loader.py`: Bot initialization and configuration
  - `manage_bot.py`: Process management utilities
  - `assets/`: Static files like images and logos
  - `handlers/`: Message and callback handling logic
  - `keyboards/`: Telegram keyboard definitions
  - `states/`: Finite state machine states
  - `utils/`: Helper functions and utilities
  - `filters/`: Custom middleware and filters

- `tests/`: All test-related files
  - `unit/`: Unit test cases
  - `integration/`: Integration test suites
  - `functional/`: End-to-end test scenarios
  - `run_tests.py`: Test runner with coverage reporting
  - `test_bot.py`: Bot-specific tests
  - `pytest.ini`: Test configuration

- `data/`: Data storage
  - `database.db`: SQLite database file

- `docs/`: Project documentation
- `run/`: Runtime files and process information

## User Flow

1. Start the Bot (`/start`)
   - New users: Select role (Customer/Admin)
   - Existing users: Directed to role-specific menu
2. Customer Flow:
   - Browse catalog via "🌿 Products"
   - Add items to cart
   - Manage cart quantities
   - Checkout with shipping details
   - Track orders
   - Contact support (max 3 pending questions)
3. Admin Flow:
   - Access admin panel with `/menu`
   - Manage products and categories
   - View and process orders
   - Handle customer inquiries

## Testing

The project includes comprehensive testing capabilities:

### Test Files
- `test_admin.py`: Admin functionality tests
  - Admin menu access control
  - Product management operations
  - Order viewing and management
  - Customer questions handling
  - Unauthorized access prevention
- `test_core.py`: Core command tests
  - Start command functionality
  - Menu navigation
  - Invalid command handling
- `run_tests.py`: Test runner with coverage reporting
- `test_bot.py`: Live API testing

### Test Database
The test suite uses a PostgreSQL test database for each test:
```python
@pytest.fixture
async def test_db():
    """Create temporary test database"""
    # Generate unique test database URL
    test_db_url = f"{DATABASE_URL}_test_{uuid.uuid4().hex[:8]}"
    test_db = PostgresDatabase(test_db_url)
    await test_db.create_tables()
    yield test_db
    # Clean up test database
    await test_db.drop_tables()
    await test_db.close()
```

### Database Schema Testing
Tests verify the correct operation of:
- Table creation and relationships
- Foreign key constraints
- Default values
- Auto-incrementing fields
- Timestamp fields

### Mock Objects
The test suite uses comprehensive mocking:
```python
@pytest.fixture
async def admin_message_mock():
    """Mock admin message"""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.answer = AsyncMock()
    # ... other mock configurations
```

### Running Tests
Run the full test suite with:
```bash
python run_tests.py
```

Or run specific test files:
```bash
# Run admin tests
python -m pytest tests/test_admin.py -v

# Run core tests
python -m pytest tests/test_core.py -v
```

### Test Coverage
The test suite includes coverage reporting for:
- Handler functions
- Database operations
- Utility functions
- State management
- Error handling

### Continuous Integration
Tests are automatically run on:
- Pull requests
- Main branch commits
- Release tags

## Testing the Bot

This project includes two testing tools to verify your bot is functioning correctly:

### 1. API-Based Testing (Recommended)

The `test_bot_api.py` script tests your bot through the official Telegram API. This is the preferred testing method, especially for Railway deployments.

```bash
python test_bot_api.py YOUR_BOT_TOKEN CHAT_ID
```

This script:
- Verifies the bot is online and responding
- Sends test commands (/start, /menu)
- Confirms the commands were successfully sent

Since this works through Telegram's official API, it will work even if direct webhook access is restricted.

### 2. Webhook Testing (Limited with Railway)

The `test_webhook.py` script attempts to test your webhook endpoint directly by simulating Telegram updates.

```bash
python test_webhook.py
```

**Note**: This method often fails with Railway deployments due to Railway's edge routing limitations. If you see 404 errors, use the API-based testing method instead.

### Continuous Integration

In CI/CD pipelines, use the API-based testing script to verify your bot is functioning after deployment:

```bash
# Example CI command
BOT_TOKEN=your_token CHAT_ID=your_id python test_bot_api.py
```

## Webhook Debugging

The bot comes with a simple webhook testing tool that allows you to send commands to your bot via the webhook and see the responses directly in Telegram.

### Features

- Send commands to your bot via webhook
- Send callback queries to simulate button presses
- Receive confirmation messages in Telegram
- See webhook response times and status codes

### Using the Webhook Tester

You can use the `webhook_logger.py` script to test your webhook:

```bash
# Basic test - send a /start command
./webhook_logger.py https://your-webhook-url/webhook 123456789 "/start"

# Send a command with notification in Telegram
./webhook_logger.py https://your-webhook-url/webhook 123456789 "/menu" --token YOUR_BOT_TOKEN

# Test a callback query (button click)
./webhook_logger.py https://your-webhook-url/webhook 123456789 "callback_data" --callback --token YOUR_BOT_TOKEN

# Show verbose output including request/response details
./webhook_logger.py https://your-webhook-url/webhook 123456789 "/start" --verbose
```

### Real Example

To test the bot currently deployed on Railway:

```bash
./webhook_logger.py https://greenelevetortelegrambottest-production.up.railway.app/webhook 238038462 "/start" --token 8012235294:AAFdgixVaHU9KeMTdyoiFtUSHDSNChHJ2Qo
```

### Checking Webhook Status

You can check the status of your webhook using:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

### Troubleshooting Webhook Issues

If you're experiencing issues with your webhook:

1. Make sure your webhook endpoint is publicly accessible
2. Verify that your webhook URL is correctly set in Telegram
3. Check for error responses in the webhook tester output
4. Confirm that you receive messages in Telegram after running the webhook test

## Important Development Notes

### Railway Database Connection

When connecting to a Railway PostgreSQL database:

1. **Always check the Railway UI for the correct connection strings**
   - Each PostgreSQL instance has two connection strings visible in the Variables section:
     - `DATABASE_URL`: For internal connections (within Railway services)
     - `DATABASE_PUBLIC_URL`: For external connections (from your local machine)

2. **Use Variable References to connect services**
   - When connecting a bot service to a database service, use the "Variable Reference" feature
   - This automatically shares all the necessary connection details between services
   - Click "Looking to connect a database? Add a Variable Reference" in the service Variables tab

3. **Troubleshooting connections**
   - If a service can't connect to the database, check that the correct connection string is being used
   - Internal services should use the internal connection string format
   - Local development should use the public connection string
   - Always verify connection strings after creating a new database instance