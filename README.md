# KAF Standalone Demo - Multi-Page Developer Guide

A comprehensive Python code sample demonstrating how to implement Kaltura's various live session functionalities. This developer guide provides working code examples for creating and managing Kaltura entries, rooms, PIDs, and different types of live events using the Kaltura Application Framework (KAF).

## 🎯 Purpose

This project serves as a **reference implementation** for developers who want to integrate different Kaltura live streaming capabilities into their own platforms. It demonstrates:

- **DIY Live Sessions**: Interactive room creation with live entry generation
- **Webcast Events**: Traditional live streaming without interactive features
- **Interactive Rooms**: Pure room creation for collaborative sessions
- **PID Provisioning**: Automated partner setup with required modules
- **Session Management**: Secure token generation for embedded components
- **API Integration Patterns**: Best practices for integrating with Kaltura's REST APIs

## 📁 Project Structure

```
kaf-standalone-demo/
├── lib/
│   ├── server.py                 # Flask application with route serving
│   ├── routes.py                 # API route definitions
│   ├── models/
│   │   ├── base_model.py         # Base model with shared functionality
│   │   ├── live_event_model.py   # Live stream operations
│   │   ├── room_model.py         # Room creation operations
│   │   └── sub_tenant_model.py   # PID and category management
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
│       ├── create-sub-tenant/    # PID creation interface
│       ├── entry-diy/            # DIY live session creation
│       ├── entry-webcast/        # Webcast event creation
│       └── entry-interactive/    # Interactive room creation
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
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

4. **Start the server**
   ```bash
   python run.py
   ```

5. **Access the application**
   - **Main Navigation**: http://localhost:3033/ (navigation hub)
   - **Create Sub-Tenant**: http://localhost:3033/create-sub-tenant
   - **DIY Live Sessions**: http://localhost:3033/entry-diy
   - **Webcast Events**: http://localhost:3033/entry-webcast
   - **Interactive Rooms**: http://localhost:3033/entry-interactive

---

## 🎥 Use Case 1: DIY Live Sessions (`/entry-diy`)

### Purpose
Create interactive DIY (Do-It-Yourself) live sessions that combine Studio (room) creation with live entry generation.

### Key Features
- **Combined Creation**: Creates both a room AND a live entry in one operation
- **Studio Mode**: Open Kaltura room in new window for interactive sessions
- **Player Mode**: Load video player inline for viewing
- **Session Management**: Generate secure Kaltura sessions with custom parameters
- **Real-time Logging**: Comprehensive operation tracking

### Environment Variables Required

```bash
# Template Configuration
TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id
```

**Note:** This will define the configuration of the studio room. Please contact your Kaltura contact for this value.

### Workflow
1. **Create Room with Live Entry**: Generates both room and live stream entry
2. **Session Generation**: Create secure sessions for Studio or Player modes
3. **Studio Mode**: Opens interactive room in new window
4. **Player Mode**: Loads video player inline for viewing

### API Endpoints
- `POST /api/kaltura/create-room-with-live`: Combined room and live entry creation
- `POST /api/kaltura/generate-session`: Session generation for Studio/Player modes
- `POST /api/kaltura/session-detail`: Fetch entry details

### UI Features
- **3-Column Layout**: Creation forms, video player, session controls
- **Mode Toggle**: Switch between Studio and Player modes
- **Real-time Logs**: Operation tracking with JSON display
- **Credential Management**: localStorage integration

---

## 📺 Use Case 2: Webcast Events (`/entry-webcast`)

### Purpose
Create traditional live streaming events without interactive room features.

### Key Features
- **Live Event Creation**: Creates only live stream entries (no rooms)
- **Player Integration**: Load video player inline for viewing
- **Session Management**: Generate secure sessions for video playback
- **No Environment Variables**: Works entirely with localStorage credentials

### Environment Variables Required

**None required** - This use case works entirely with credentials stored in localStorage from the PID creation process.

### Workflow
1. **Create Live Event**: Generates only a live stream entry
2. **Session Generation**: Create secure sessions for video playback
3. **Player Loading**: Loads video player inline for viewing

### API Endpoints
- `POST /api/kaltura/add-live`: Live event creation only
- `POST /api/kaltura/generate-session`: Session generation for video playback
- `POST /api/kaltura/session-detail`: Fetch entry details

### UI Features
- **3-Column Layout**: Creation forms, video player, session controls
- **Player Mode Only**: Focused on video playback
- **Real-time Logs**: Operation tracking with JSON display
- **Credential Management**: localStorage integration

---

## 🎮 Use Case 3: Interactive Rooms (`/entry-interactive`)

### Purpose
Create pure interactive rooms for collaborative sessions based on web-rtc

### Key Features
- **Room-Only Creation**: Creates only interactive rooms (no live entries)
- **Inline Room Loading**: Load interactive room directly in the page
- **Session Management**: Generate secure sessions for room access
- **Moderator Controls**: Chat and room moderation settings
- **localStorage Credentials**: Uses credentials from PID creation process

### Environment Variables Required

```bash
# Template Configuration
TEMPLATE_ROOM_ENTRY_ID=your_template_room_entry_id
```

**Note:** This will define the configuration of the room. Please contact your Kaltura contact for this value.

### Workflow
1. **Create Room**: Generates only an interactive room
2. **Session Generation**: Create secure sessions for room access
3. **Inline Loading**: Loads interactive room directly in the page

### API Endpoints
- `POST /api/kaltura/add-room`: Room creation only
- `POST /api/kaltura/generate-session`: Session generation for room access
- `POST /api/kaltura/session-detail`: Fetch room details

### UI Features
- **3-Column Layout**: Creation forms, room player, session controls
- **Inline Room Loading**: Interactive room loads directly in the page
- **Moderator Fields**: Chat and room moderation controls
- **Real-time Logs**: Operation tracking with JSON display
- **Credential Management**: localStorage integration

---

## 🏢 Use Case 4: Sub-Tenant Creation (`/create-sub-tenant`)

### Purpose
Automated creation of new Kaltura partners with pre-configured KAF modules and publishing categories.

### Key Features
- **One-Click Partner Creation**: Automated workflow with no manual input required
- **KAF Module Configuration**: Pre-configured with all required KAF modules
- **Category Hierarchy Setup**: Automatic creation of publishing categories
- **Credential Management**: Automatic localStorage population for cross-page usage
- **Real-time Progress Tracking**: Server-Sent Events for operation status

### Environment Variables Required

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

# Customer Configuration
CUSTOMER_NAME=YourCompanyName
```

### Workflow
1. **Create Partner**: Register new partner with all required modules
2. **Monitor KAF**: Wait for KAF instance to become ready
3. **Create Category**: Set up publishing category under customer hierarchy
4. **Store Credentials**: Save all credentials to localStorage for other pages

### API Endpoints
- `POST /api/kaltura/create-sub-tenant`: Complete PID creation workflow
- `POST /api/kaltura/create-publishing-category`: Category management
- `GET /api/kaltura/progress-stream`: Real-time progress updates

---

## 🔧 Configuration

### Environment Variable Setup

**Note**: Environment variables are only required for Sub-Tenant Creation, DIY, and Interactive Room use cases. The Webcast use case works entirely with localStorage credentials from the PID creation process.



### Credential Management
- **localStorage Persistence**: Credentials saved in browser for convenience
- **Cross-Page Sync**: Automatic credential sharing between interfaces
- **Real-time Updates**: Form changes immediately update localStorage

### Local Storage Keys (for demo purpose only)
- `tenantId`: PID
- `tenantEmail`: Admin user email
- `adminSecret`: Admin secret
- `publishingCategoryId`: Default category for entries (only for live entries)
- `kalturaUrl`: Service URL

---

## 📦 Dependencies

```python
Flask==2.3.3              # Web framework
python-dotenv==1.0.0       # Environment variable support
requests==2.31.0           # HTTP client for KAF API calls
pycryptodome==3.19.0       # Cryptographic functions
KalturaApiClient==21.19.0  # Official Kaltura Python client
lxml==6.0.0               # XML processing for metadata
```

---

## 🐛 Troubleshooting

### Common Issues
1. **Session Creation Fails**: Verify admin secret and PID
2. **Room Creation Errors**: Ensure template room entry ID is valid
3. **Metadata Issues**: Check if KwebcastProfile exists in your PID
4. **CORS Errors**: Ensure proper Kaltura URL configuration
5. **KAF Instance Not Ready**: Wait for KAF instance to become available

### Debug Tools
- Browser Developer Tools for JavaScript debugging
- Flask debug output in terminal
- Real-time logs in each interface
- Network tab for API request/response inspection

---

## 📄 License

This project is a comprehensive port and enhancement of the original Kaltura KAF standalone demo. Please refer to Kaltura's licensing terms for usage restrictions.

---


## 🆘 Support

For technical issues:
- Check the real-time logs in the application interface
- Verify Kaltura credentials and PID configuration
- Consult Kaltura's official documentation for API-specific questions
- Review browser console for JavaScript errors

For Kaltura-specific questions, please refer to the official Kaltura documentation or contact Kaltura support. 