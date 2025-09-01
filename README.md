# KAF Standalone Demo - Developer Guide

A comprehensive Python code sample demonstrating how to implement Kaltura's DIY (Do-It-Yourself) live session functionality. This developer guide provides working code examples for creating and managing Kaltura entries, rooms, and sub-tenants using the Kaltura Application Framework (KAF).

## 🎯 Purpose

This project serves as a **reference implementation** for developers who want to integrate Kaltura's DIY live streaming capabilities into their own platforms. It demonstrates:

- **Live Stream Creation**: How to programmatically create Kwebcast live entries
- **Room Management**: How to create and configure embedded rooms
- **Session Generation**: How to generate secure Kaltura sessions for users
- **Sub-tenant Provisioning**: How to set up new Kaltura partners with required modules
- **API Integration Patterns**: Best practices for integrating with Kaltura's REST APIs

## 🚀 Key Features for Developers

### 🎥 DIY Live Session Implementation
- **Live Entry Creation**: Complete code sample for creating Kwebcast live streams
- **Metadata Management**: Automatic attachment of KwebcastProfile metadata
- **DVR Configuration**: Programmatic setup of recording and playback options
- **Category Publishing**: Integration with Kaltura for entitlments

### 🏢 Sub-tenant Management
- **Partner Provisioning**: Full code example for creating new Kaltura partners
- **Module Configuration**: Pre-configured with essential KAF modules
- **Category Hierarchy**: Automatic creation of publishing categories
- **Template Support**: Reusable partner and room templates

### 🎛️ API Integration Examples
- **Service Layer Pattern**: Clean separation of concerns with dedicated models
- **Error Handling**: Comprehensive error management and logging
- **Session Management**: Secure token generation for embedded components
- **Real-time Feedback**: Progress tracking and status updates

## 📁 Project Structure

```
kaf-standalone-demo/
├── lib/
│   ├── server.py                 # Flask application with route serving
│   ├── routes.py                 # API route definitions (7 endpoints)
│   ├── models/
│   │   ├── base_model.py         # Base model with shared functionality
│   │   ├── live_event_model.py   # Live stream operations
│   │   ├── room_model.py         # Room creation operations
│   │   └── sub_tenant_model.py   # Sub-tenant and category management
│   ├── services/
│   │   └── kaltura_service.py    # Service layer for API operations
│   └── kaltura_integration/
│       └── simple_client.py      # Enhanced Kaltura client wrapper
├── public/
│   ├── index.html                # Main navigation interface
│   ├── app.js                    # Shared utilities and navigation
│   ├── app.css                   # Global styles
│   ├── en.json                   # Localization data
│   └── pages/
│       ├── entry-create-kaf/     # Enhanced entry creation interface
│       │   ├── index.html        # 3-column responsive layout
│       │   ├── app.js            # Advanced form handling & player integration
│       │   └── app.css           # Custom styling (500+ lines)
│       └── create-sub-tenant/    # Sub-tenant creation interface
│           ├── index.html        # Multi-step creation form
│           └── app.js            # Automated tenant setup workflow
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── list_metadata_profiles.py     # Utility for metadata profile discovery
└── README.md                     # This documentation
```


## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kaf-standalone-demo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Environment Variables

The application requires several environment variables to be set for proper operation:

### Required Environment Variables

```bash
# Kaltura Configuration
KALTURA_URL=https://www.kaltura.com
KALTURA_PARENT_PARTNER_ID=your_parent_partner_id
KALTURA_ADMIN_SECRET=your_admin_secret
KALTURA_USER_ID=your_user_id

# Partner Configuration
KALTURA_PARTNER_NAME=your_partner_name
KALTURA_PARTNER_EMAIL=admin@yourpartner.com
KALTURA_PARTNER_DESCRIPTION=your_partner_description
KALTURA_TEMPLATE_PARTNER_ID=your_template_partner_id

# Template Room Entry ID for room creation
TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id

# Customer Configuration
CUSTOMER_NAME=YourCompanyName

# Flask Configuration (optional, defaults shown)
FLASK_HOST=0.0.0.0
FLASK_PORT=3033
FLASK_DEBUG=False
```

### Setting Environment Variables

**Option 1: Export in shell**
```bash
export KALTURA_URL=https://www.kaltura.com
export KALTURA_PARENT_PARTNER_ID=your_parent_partner_id
export KALTURA_ADMIN_SECRET=your_admin_secret
export KALTURA_USER_ID=your_user_id
export KALTURA_PARTNER_NAME="your_partner_name"
export KALTURA_PARTNER_EMAIL=admin@yourpartner.com
export KALTURA_PARTNER_DESCRIPTION="your_partner_description"
export KALTURA_TEMPLATE_PARTNER_ID=your_template_partner_id
export TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id
export CUSTOMER_NAME=YourCompanyName
```

**Option 2: Create .env file**
```bash
# Create .env file in project root
echo "KALTURA_URL=https://www.kaltura.com" > .env
echo "KALTURA_PARENT_PARTNER_ID=your_parent_partner_id" >> .env
echo "KALTURA_ADMIN_SECRET=your_admin_secret" >> .env
echo "KALTURA_USER_ID=your_user_id" >> .env
echo "KALTURA_PARTNER_NAME=your_partner_name" >> .env
echo "KALTURA_PARTNER_EMAIL=admin@yourpartner.com" >> .env
echo "KALTURA_PARTNER_DESCRIPTION=your_partner_description" >> .env
echo "KALTURA_TEMPLATE_PARTNER_ID=your_template_partner_id" >> .env
echo "TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id" >> .env
echo "CUSTOMER_NAME=YourCompanyName" >> .env
```

**Option 3: Set in your IDE/terminal**
```bash
TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id python run.py
```

## 🚀 Usage

### Quick Setup
Run the interactive setup script to configure your environment:
```bash
python setup_env.py
```

1. **Start the server**
   ```bash
   python run.py
   ```
   Or alternatively:
   ```bash
   cd lib
   python server.py
   ```

2. **Access the application**
   - **Main Application**: http://localhost:3033/ (navigation hub)
   - **Entry Create KAF**: http://localhost:3033/entry-create-kaf (primary interface)
   - **Create Sub Tenant**: http://localhost:3033/create-sub-tenant (tenant management)

3. **Initial Setup**
   - Start with the **Create Sub Tenant** page to set up your Kaltura partner
   - Credentials are automatically stored in localStorage for use across pages
   - Use the **Entry Create KAF** page for content creation and management



## 🔧 Configuration

### Customer Name Configuration
The application uses a configurable customer name for category hierarchy. Set this via environment variable:

```bash
# Set customer name (defaults to "customer_name" if not set)
export CUSTOMER_NAME=YourCompanyName

# Or in .env file
CUSTOMER_NAME=YourCompanyName
```

This value is used to create the category hierarchy: `{CUSTOMER_NAME}>site>channels`

**Note**: If no `CUSTOMER_NAME` is set, the system will default to "customer_name" as the category hierarchy.

### Credential Management
- **No Environment Variables**: All configuration via frontend forms
- **localStorage Persistence**: Credentials saved in browser for convenience
- **Cross-Page Sync**: Automatic credential sharing between interfaces
- **Real-time Updates**: Form changes immediately update localStorage

### Required Credentials
- **Partner ID**: Your Kaltura partner ID
- **Admin Secret**: Partner admin secret
- **User ID**: Admin user ID for operations
- **Kaltura URL**: Service URL (default: https://www.kaltura.com)
- **Template Partner ID**: For sub-tenant creation
- **Template Room Entry ID**: For room creation in Studio mode

### Local Storage Keys dont expose in UI! (for demo purpose only)
- `tenantId`: Partner ID
- `tenantEmail`: Admin user email
- `adminSecret`: Admin secret
- `publishingCategoryId`: Default category for entries
- `kalturaUrl`: Service URL

## 🎨 User Interface Guide

### Entry Create KAF Interface

#### Left Column - Creation Forms
- **Creation Mode Toggle**: Switch between Broadcast (live entries) and Studio (rooms)
- **Entry/Room Form**: Dynamic form adapting to selected mode
- **Entry Details**: Fetch information for existing entries
- **Activity Logs**: Real-time operation logging with JSON display

#### Middle Column - Video Player
- **Full-Screen Video**: Embedded Kaltura player/studio interface
- **Responsive Design**: Adapts to different screen sizes
- **Direct Integration**: Seamless loading of generated sessions

#### Right Column - Session Controls
- **Mode Toggle**: Switch between Studio (room creation) and Player (viewing)
- **Session Generation**: Create Kaltura sessions with custom parameters
- **Role Management**: Configure user roles and privileges
- **LocalStorage Manager**: View and edit stored credentials

### Create Sub Tenant Interface
- **Step-by-Step Process**: Guided tenant creation workflow
- **Automatic Setup**: Category creation and module configuration
- **Progress Feedback**: Real-time status updates and error handling
- **Credential Export**: Automatic localStorage population for other pages

## 🔧 Sub-Tenant Creation Implementation

### Overview
The application provides a complete implementation for creating Kaltura sub-tenants with automatic module configuration and KAF instance setup. This replaces the need for manual API calls and curl commands.

### Core Implementation Files

#### Backend Models (`lib/models/sub_tenant_model.py`)
The `KalturaSubTenantModel` class handles all sub-tenant operations:

- **Partner Registration**: Uses `partner->register` API with proper module configuration
- **Module Management**: Automatically enables required KAF modules via `additionalParams`
- **KAF Instance Monitoring**: Checks instance readiness with retry logic


#### Service Layer (`lib/services/kaltura_service.py`)
The `KalturaService.create_sub_tenant()` method orchestrates the entire process:

- **Environment Configuration**: Reads credentials from environment variables
- **Multi-Step Workflow**: Creates tenant → waits for KAF → creates category → runs automation
- **Progress Tracking**: Real-time updates via Server-Sent Events
- **Error Handling**: Comprehensive error management with fallbacks

#### API Endpoints (`lib/routes.py`)
RESTful endpoints for sub-tenant operations:

- `POST /api/kaltura/create-sub-tenant`: Complete tenant creation workflow
- `POST /api/kaltura/create-publishing-category`: Category management
- `GET /api/kaltura/progress-stream`: Real-time progress updates

#### Frontend Interface (`public/pages/create-sub-tenant/`)
User interface for triggering sub-tenant creation:

- **Single-Click Creation**: Automated workflow with no manual input required
- **Credential Storage**: Automatic localStorage population for cross-page usage
- **Result Display**: JSON response formatting with success/error handling

### Module Configuration

The system automatically configures the following KAF modules during partner creation:

**Module List**: See `lib/models/sub_tenant_model.py` lines 108-109 for the complete list of enabled modules.

**Module Activation**: See `lib/models/sub_tenant_model.py` lines 115-125 for how modules are enabled via `additionalParams` with both the module list and individual enable flags.

### KAF Instance Readiness Monitoring

Instead of manual curl commands, the system automatically monitors KAF instance readiness:

**Instance Check Method**: See `lib/models/sub_tenant_model.py` lines 280-300 for the `check_kaf_instance_ready()` method that replaces manual curl calls to the version endpoint.

**Intelligent Polling**: See `lib/services/kaltura_service.py` lines 480-520 for the service layer implementation with configurable timeouts and retry logic.



### Publishing Category Creation

The system automatically creates a publishing category under the standard hierarchy:

**Category Creation**: See `lib/models/sub_tenant_model.py` lines 200-250 for the `create_publishing_category()` method that automatically locates the customer category hierarchy parent and creates the publishing category.

### Usage Example

To create a sub-tenant, simply navigate to the Create Sub Tenant page and click the create button. The system will:

1. **Create Partner**: Register new partner with all required modules
2. **Monitor KAF**: Wait for KAF instance to become ready
3. **Create Category**: Set up publishing category under the customer category hierarchy
4. **Store Credentials**: Save all credentials to localStorage for other pages

### Environment Variables Required

```bash
# Required for sub-tenant creation
KALTURA_PARENT_PARTNER_ID=your_parent_partner_id
KALTURA_ADMIN_SECRET=your_admin_secret
KALTURA_USER_ID=your_user_id
KALTURA_URL=https://www.kaltura.com
KALTURA_TEMPLATE_PARTNER_ID=your_template_partner_id
KALTURA_PARTNER_NAME=your_partner_name
KALTURA_PARTNER_EMAIL=admin@yourpartner.com
KALTURA_PARTNER_DESCRIPTION=your_partner_description
```

### Benefits Over Manual Implementation

- **No Manual API Calls**: Complete automation of the entire workflow
- **Built-in Retry Logic**: Intelligent polling for KAF instance readiness
- **Progress Tracking**: Real-time updates via Server-Sent Events
- **Error Handling**: Comprehensive error management with fallbacks
- **Credential Management**: Automatic storage and sharing across interfaces
- **Module Configuration**: Pre-configured with all required KAF modules

## 📦 Dependencies

```python
Flask==2.3.3              # Web framework
python-dotenv==1.0.0       # Environment variable support
requests==2.31.0           # HTTP client for KAF API calls
pycryptodome==3.19.0       # Cryptographic functions
KalturaApiClient==21.19.0  # Official Kaltura Python client
lxml==6.0.0               # XML processing for metadata
```

## 🐛 Troubleshooting

### Common Issues
1. **Session Creation Fails**: Verify admin secret and partner ID
2. **Room Creation Errors**: Ensure template room entry ID is valid
3. **Metadata Issues**: Check if KwebcastProfile exists in your partner account
4. **CORS Errors**: Ensure proper Kaltura URL configuration

### Debug Tools
- Browser Developer Tools for JavaScript debugging
- Flask debug output in terminal
- Real-time logs in the Entry Create KAF interface
- Network tab for API request/response inspection

## 📄 License

This project is a comprehensive port and enhancement of the original Kaltura KAF standalone demo. Please refer to Kaltura's licensing terms for usage restrictions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Test thoroughly with your Kaltura partner account
4. Submit a pull request with detailed description

## 🆘 Support

For technical issues:
- Check the real-time logs in the application interface
- Verify Kaltura credentials and partner configuration
- Consult Kaltura's official documentation for API-specific questions
- Review browser console for JavaScript errors

For Kaltura-specific questions, please refer to the official Kaltura documentation or contact Kaltura support. 