/**
 * Initialize all event listeners when the DOM is fully loaded.
 * This sets up handlers for form submissions and button clicks.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Interactive Room page...');
    
    // Check if all required elements exist
    const requiredElements = {
        roomForm: document.getElementById('roomForm'),
        closeModal: document.getElementById('closeModal'),
        getRoomForm: document.getElementById('getRoomForm'),
        clearLogsBtn: document.getElementById('clearLogsBtn'),
        loadRoomBtn: document.getElementById('loadRoomBtn'),
        roomSessionForm: document.getElementById('roomSessionForm'),
        moderatorFields: document.getElementById('moderatorFields'),
        createButton: document.getElementById('createButton')
    };

    // Log any missing elements
    const missingElements = Object.entries(requiredElements)
        .filter(([name, element]) => !element)
        .map(([name]) => name);

    if (missingElements.length > 0) {
        console.error('❌ Missing required elements:', missingElements);
        return;
    }

    console.log('✅ All required elements found');

    // Room form handler - creates only rooms (no live entries)
    const roomForm = requiredElements.roomForm;
    roomForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('📝 Room form submitted - creating interactive room...');
        await handleCreateRoom();
    });

    const closeModal = requiredElements.closeModal;
    closeModal.addEventListener('click', () => {
        const modalDialog = document.getElementById('modalDialog');
        if (modalDialog) {
            modalDialog.style.display = 'none';
        }
    });

    const getRoomForm = requiredElements.getRoomForm;
    getRoomForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleShowRoomDetails();
    });

    const clearLogsBtn = requiredElements.clearLogsBtn;
    clearLogsBtn.addEventListener('click', () => {
        const logOutput = document.getElementById('logOutput');
        if (logOutput) {
            logOutput.textContent = '';
        }
    });

    // Room session form handler - loads room inline
    const loadRoomBtn = requiredElements.loadRoomBtn;
    const roomSessionForm = requiredElements.roomSessionForm;

    loadRoomBtn.addEventListener('click', async function() {
        await handleLoadRoom();
    });

    // LocalStorage functionality
    initializeLocalStorageDisplay();
    setupLocalStorageEventListeners();
    
    console.log('✅ Event listeners initialized successfully');
});

/**
 * Handles room creation (only room, no live entry).
 * @returns {Promise<void>}
 * @throws {Error} If the room creation fails
 */
async function handleCreateRoom() {
    try {
        // Clear previous logs
        const logOutput = document.getElementById('logOutput');
        if (logOutput) {
            logOutput.textContent = '';
        }
        
        // Validate form elements
        const roomNameElement = document.getElementById('roomName');
        const roomDescriptionElement = document.getElementById('roomDescription');

        // Check if elements exist
        if (!roomNameElement || !roomDescriptionElement) {
            throw new Error('Room form elements not found. Please refresh the page and try again.');
        }

        const roomName = roomNameElement.value;
        const roomDesc = roomDescriptionElement.value;
        
        // Check if required fields have values
        if (!roomName.trim() || !roomDesc.trim()) {
            throw new Error('Room name and description are required fields.');
        }

        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        
        if (!tenantCredentials.id || !tenantCredentials.adminSecret) {
            throw new Error('Missing tenant credentials. Please set up your PID and Secret in the credentials section.');
        }
        
        logMessage('🚀 Creating interactive room...');
        
        // Make API request to create only a room (no live entry)
        const response = await fetch('/api/kaltura/add-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomName,
                roomDesc,
                partnerId: tenantCredentials.id,
                adminSecret: tenantCredentials.adminSecret,
                userId: tenantCredentials.email,
                kalturaUrl: getKalturaUrl()
            })
        });
        
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to create room');
        }

        if (data.success) {
            logMessage('✅ Room created successfully!');
            logDataMessage(data.room);
            
            // Auto-fill the room ID in the session form
            const roomIdField = document.getElementById('roomId');
            if (roomIdField && data.room && data.room.id) {
                roomIdField.value = data.room.id;
                logMessage(`📝 Room ID ${data.room.id} has been auto-filled in the session form.`);
            }
        } else {
            throw new Error(data.message || 'Failed to create room');
        }

        // Clear form after successful creation
        roomNameElement.value = '';
        roomDescriptionElement.value = '';
        
    } catch (error) {
        console.error('❌ Error creating room:', error);
        logMessage('❌ Error creating room: ' + error.message);
    }
}

/**
 * Logs a message to the UI log output area.
 * @param {string} message - The message to log
 */
function logMessage(message) {
    const logOutput = document.getElementById('logOutput');
    if (logOutput) {
        logOutput.textContent += message + '\n';
    } else {
        console.log('Log output element not found:', message);
    }
}

/**
 * Logs a structured data object to the UI log output area.
 * @param {Object} message - The data object to log
 */
function logDataMessage(message) {
    const logOutput = document.getElementById('logOutput');
    if (logOutput) {
        logOutput.textContent += JSON.stringify(message, null, 2) + '\n';
    } else {
        console.log('Log output element not found:', message);
    }
}

/**
 * Fetches and displays details for a specific room.
 * @returns {Promise<void>}
 * @throws {Error} If fetching room details fails
 */
async function handleShowRoomDetails() {
    try {
        const roomIdElement = document.getElementById('roomIdInput');
        
        // Check if element exists
        if (!roomIdElement) {
            throw new Error('Room ID input element not found. Please refresh the page and try again.');
        }

        const roomId = roomIdElement.value;
        
        // Check if required field has value
        if (!roomId.trim()) {
            throw new Error('Room ID is required. Please enter a Room ID.');
        }

        logMessage('Fetching details from Room ID ' + roomId + '...');
        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        
        const response = await fetch('/api/kaltura/session-detail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                entryId: roomId, 
                partnerId: tenantCredentials.id,
                adminSecret: tenantCredentials.adminSecret,
                userId: tenantCredentials.email,
                kalturaUrl: getKalturaUrl() 
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch room details');
        }

        const data = await response.json();
        logDataMessage(data);
    } catch (error) {
        console.error('Error fetching room details:', error);
        logMessage('Error fetching room details: ' + error.message);
        alert('Error fetching room details: ' + error.message);
    }
}

/**
 * Handles loading room inline in the page (not in new window).
 * @returns {Promise<void>}
 */
async function handleLoadRoom() {
    try {
        // Get all form elements with null checks
        const userIdElement = document.getElementById('userId');
        const roomIdElement = document.getElementById('roomId');
        const roleElement = document.getElementById('role');
        const firstNameElement = document.getElementById('firstName');
        const lastNameElement = document.getElementById('lastName');
        const chatModeratorElement = document.getElementById('chatModerator');
        const roomModeratorElement = document.getElementById('roomModerator');

        // Check if required elements exist
        if (!userIdElement || !roomIdElement || !roleElement) {
            throw new Error('Required form elements not found. Please refresh the page and try again.');
        }

        // Check if required fields have values
        if (!userIdElement.value.trim() || !roomIdElement.value.trim()) {
            throw new Error('userId and roomId are required fields. Please fill them in.');
        }

        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        
        // Generate the Kaltura session
        const sessionResponse = await fetch('/api/kaltura/generate-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: userIdElement.value,
                entryId: roomIdElement.value, // Use roomId as entryId for session generation
                role: roleElement.value,
                firstName: firstNameElement ? firstNameElement.value : '',
                lastName: lastNameElement ? lastNameElement.value : '',
                chatModerator: chatModeratorElement ? chatModeratorElement.value : '',
                roomModerator: roomModeratorElement ? roomModeratorElement.value : '',
                partnerId: tenantCredentials.id,
                adminSecret: tenantCredentials.adminSecret,
                kalturaUrl: getKalturaUrl()
            })
        });

        if (!sessionResponse.ok) {
            const errorData = await sessionResponse.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${sessionResponse.status}: Failed to generate session`);
        }

        const sessionData = await sessionResponse.json();
        
        if (!sessionData.success) {
            // Provide more specific error handling
            let errorMessage = sessionData.message || 'Failed to generate session';
            if (sessionData.error === 'START_SESSION_ERROR') {
                errorMessage = `Session creation failed for partner ${tenantCredentials.id}. Please verify your admin secret and user ID are correct.`;
            } else if (sessionData.error === 'INVALID_SESSION_PARAMS') {
                errorMessage = `Invalid session parameters for partner ${tenantCredentials.id}. Please check your credentials.`;
            } else if (sessionData.error === 'PARTNER_CONFIG_ERROR') {
                errorMessage = `Partner configuration error for partner ${tenantCredentials.id}. Please verify your partner ID.`;
            }
            throw new Error(errorMessage);
        }

        // Log the session data
        logMessage('Generated Kaltura Session for Interactive Room:');
        logDataMessage(sessionData.session);

        // Build the embedded rooms URL with the KS in the path
        const fullUrl = `https://${tenantCredentials.id}.kaf.kaltura.com/embeddedrooms/index/view-room/ks/${sessionData.session.ks}`;
        
        // Load the room in the iframe (inline, not new window)
        const roomPlayerIframe = document.getElementById('roomPlayerIframe');
        if (roomPlayerIframe) {
            roomPlayerIframe.src = fullUrl;
            logMessage('✅ Interactive room loaded inline in the page');
        } else {
            logMessage('Error: Room player iframe not found');
        }
        
        logMessage('Generated Room URL: ' + fullUrl);
    } catch (error) {
        console.error('Error loading room:', error);
        logMessage('Error loading room: ' + error.message);
    }
}

// Add utility to get Kaltura URL from form or localStorage
function getKalturaUrl() {
    return localStorage.getItem('kalturaUrl') || 'https://www.kaltura.com';
}

// Utility to get tenant credentials from the form or localStorage
function getTenantCredentials() {
    return {
        id: localStorage.getItem('tenantId') || '',
        email: localStorage.getItem('tenantEmail') || '',
        adminSecret: localStorage.getItem('adminSecret') || '',
        kalturaUrl: getKalturaUrl()
    };
}

/**
 * Initialize localStorage display by populating fields with current values
 */
function initializeLocalStorageDisplay() {
    const localStorageFields = {
        'localTenantId': 'tenantId',
        'localTenantEmail': 'tenantEmail', 
        'localAdminSecret': 'adminSecret',
        'localPublishingCategoryId': 'publishingCategoryId'
    };

    // Populate fields with current localStorage values
    Object.entries(localStorageFields).forEach(([elementId, storageKey]) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.value = localStorage.getItem(storageKey) || '';
        }
    });
}

/**
 * Set up event listeners for localStorage management buttons
 */
function setupLocalStorageEventListeners() {
    // Update localStorage button
    const updateButton = document.getElementById('updateLocalStorage');
    if (updateButton) {
        updateButton.addEventListener('click', updateLocalStorageFromForm);
    }

    // Clear localStorage button  
    const clearButton = document.getElementById('clearLocalStorage');
    if (clearButton) {
        clearButton.addEventListener('click', clearAllLocalStorage);
    }

    // Listen for localStorage changes from other pages
    window.addEventListener('storage', handleStorageChange);
    
    // Also listen for localStorage changes within the same window
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(key, value) {
        originalSetItem.apply(this, arguments);
        // Update display if this key affects our form
        updateLocalStorageDisplay(key, value);
    };
}

/**
 * Update localStorage from form values
 */
function updateLocalStorageFromForm() {
    const localStorageFields = {
        'localTenantId': 'tenantId',
        'localTenantEmail': 'tenantEmail',
        'localAdminSecret': 'adminSecret', 
        'localPublishingCategoryId': 'publishingCategoryId'
    };

    Object.entries(localStorageFields).forEach(([elementId, storageKey]) => {
        const element = document.getElementById(elementId);
        if (element) {
            const value = element.value.trim();
            if (value) {
                localStorage.setItem(storageKey, value);
            } else {
                localStorage.removeItem(storageKey);
            }
        }
    });

    console.log('LocalStorage updated from form');
}

/**
 * Clear all localStorage values
 */
function clearAllLocalStorage() {
    const keysToRemove = ['tenantId', 'tenantEmail', 'adminSecret', 'publishingCategoryId'];
    
    keysToRemove.forEach(key => {
        localStorage.removeItem(key);
    });

    // Clear form fields
    initializeLocalStorageDisplay();
    
    console.log('All localStorage cleared');
}

/**
 * Handle storage changes from other windows/tabs
 */
function handleStorageChange(e) {
    updateLocalStorageDisplay(e.key, e.newValue);
}

/**
 * Update specific localStorage display field
 */
function updateLocalStorageDisplay(key, value) {
    const storageToElementMap = {
        'tenantId': 'localTenantId',
        'tenantEmail': 'localTenantEmail',
        'adminSecret': 'localAdminSecret',
        'publishingCategoryId': 'localPublishingCategoryId'
    };

    const elementId = storageToElementMap[key];
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.value = value || '';
        }
    }
}