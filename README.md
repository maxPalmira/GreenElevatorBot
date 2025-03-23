<p align="center">
  <a href="https://t.me/example_store_bot"><img src="data/assets/logo.png" alt="ShopBot"></a>
</p>

# Green Elevator Wholesale Bot

A Telegram bot developed to manage cannabis wholesale operations, primarily targeting the market in Thailand. Built using the aiogram framework, this bot facilitates interactions between customers and administrators, offering a streamlined platform for browsing products, managing orders, and providing customer support.

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

### Database Schema

The bot uses SQLite with the following schema:

1. Users Table:
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

2. Categories Table:
```sql
CREATE TABLE categories (
    idx TEXT PRIMARY KEY,
    title TEXT NOT NULL
)
```

3. Products Table:
```sql
CREATE TABLE products (
    idx TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    image TEXT,
    price INTEGER,
    tag TEXT,
    FOREIGN KEY (tag) REFERENCES categories(idx)
)
```

4. Orders Table:
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(idx),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

5. Cart Table:
```sql
CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(idx),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, product_id)
)
```

6. Questions Table:
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    question TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

### Bot Architecture

The bot is built using:
- aiogram framework for Telegram Bot API
- SQLite for data storage
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

Example `.env` file:
```
BOT_TOKEN=your_bot_token_here
ADMINS=123456789,987654321
```

## Dependencies

*   `aiogram==2.25.1`: Telegram Bot API framework
*   `python-dotenv==1.0.0`: Environment variable management
*   `SQLAlchemy==2.0.23`: SQL toolkit and ORM
*   `aiohttp==3.8.6`: Asynchronous HTTP client/server
*   `Pillow==9.5.0`: Image processing
*   `python-dateutil==2.8.2`: DateTime utilities

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
│   └── database.db      # SQLite database
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
  - `run_tests.py`: Test execution script
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
The test suite uses a temporary SQLite database for each test:
```python
@pytest.fixture
async def test_db():
    """Create temporary test database"""
    db_fd, db_path = tempfile.mkstemp()
    test_db = init_test_db(db_path)
    yield test_db
    os.close(db_fd)
    os.unlink(db_path)
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
