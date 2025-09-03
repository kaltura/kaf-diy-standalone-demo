/**
 * Initialize all event listeners when the DOM is fully loaded.
 * This sets up handlers for form submissions and button clicks.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Entry Create KAF page...');
    
    // Initialize SSE connection for real-time progress updates
    initializeProgressStream();
    
    // Check if all required elements exist
    const requiredElements = {
        combinedForm: document.getElementById('combinedForm'),
        closeModal: document.getElementById('closeModal'),
        getSessionForm: document.getElementById('getSessionForm'),
        clearLogsBtn: document.getElementById('clearLogsBtn'),
        apiTestSubmit: document.getElementById('apiTestSubmit'),
        apiTestForm: document.getElementById('apiTestForm'),
        studioMode: document.getElementById('studioMode'),
        playerMode: document.getElementById('playerMode'),
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

    // Combined form handler - now only creates rooms
    const combinedForm = requiredElements.combinedForm;
    combinedForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('📝 Form submitted - creating room...');
        await handleCreateRoom();
    });

    const closeModal = requiredElements.closeModal;
    closeModal.addEventListener('click', () => {
        const modalDialog = document.getElementById('modalDialog');
        if (modalDialog) {
            modalDialog.style.display = 'none';
        }
    });

    const getSessionForm = requiredElements.getSessionForm;
    getSessionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleShowEntryDetails();
    });

    const clearLogsBtn = requiredElements.clearLogsBtn;
    clearLogsBtn.addEventListener('click', () => {
        const logOutput = document.getElementById('logOutput');
        if (logOutput) {
            logOutput.textContent = '';
        }
    });

    // Mode switching functionality for KAF KME section
    const studioMode = requiredElements.studioMode;
    const playerMode = requiredElements.playerMode;
    const moderatorFields = requiredElements.moderatorFields;

    function updateModeUI() {
        const isStudioMode = studioMode.checked;
        
        // Show/hide moderator fields
        if (moderatorFields) {
            moderatorFields.style.display = isStudioMode ? 'flex' : 'none';
        }
        
        // Update button text
        if (requiredElements.apiTestSubmit) {
            requiredElements.apiTestSubmit.textContent = isStudioMode ? 'Generate Session' : 'Load Player';
        }
        
        // Update Kaltura Room section text
        const kalturaRoomSection = document.querySelector('.right-column .section:last-child p');
        if (kalturaRoomSection) {
            if (isStudioMode) {
                kalturaRoomSection.textContent = 'Click "Generate Session" to open the Kaltura Room in a new window. You can move and resize this window as needed.';
            } else {
                kalturaRoomSection.textContent = 'Click "Load Player" to open the Kaltura Player in a new window. You can move and resize this window as needed.';
            }
        }
    }

    // Initial mode setup
    updateModeUI();

    // Mode change listeners
    if (studioMode) {
        studioMode.addEventListener('change', updateModeUI);
    }
    if (playerMode) {
        playerMode.addEventListener('change', updateModeUI);
    }

    // API Test Form logic
    const apiTestSubmit = requiredElements.apiTestSubmit;
    const apiTestForm = requiredElements.apiTestForm;

    apiTestSubmit.addEventListener('click', async function() {
        const isStudioMode = studioMode && studioMode.checked;
        
        if (isStudioMode) {
            await handleStudioMode();
        } else {
            await handlePlayerMode();
        }
    });

    // LocalStorage functionality
    initializeLocalStorageDisplay();
    setupLocalStorageEventListeners();
    
    console.log('✅ Event listeners initialized successfully');
});

/**
 * Initialize Server-Sent Events connection for real-time progress updates
 */
function initializeProgressStream() {
    const eventSource = new EventSource('/api/kaltura/progress-stream');
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            // Skip keepalive messages
            if (data.type === 'keepalive') {
                return;
            }
            
            // Log the progress update
            logMessage(data.message);
            
            // Only log data for error messages, not success summaries
            if (data.data && data.step === 'error') {
                logDataMessage(data.data);
            }
            
        } catch (error) {
            console.error('Error parsing SSE message:', error);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        // Try to reconnect after a delay
        setTimeout(() => {
            initializeProgressStream();
        }, 5000);
    };
    
    console.log('✅ SSE connection initialized for real-time progress updates');
}

/**
 * Handles room creation with automatic live entry creation.
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
        const entryNameElement = document.getElementById('entryName');
        const entryDescriptionElement = document.getElementById('entryDescription');

        // Check if elements exist
        if (!entryNameElement || !entryDescriptionElement) {
            throw new Error('Room form elements not found. Please refresh the page and try again.');
        }

        const roomName = entryNameElement.value;
        const roomDesc = entryDescriptionElement.value;
        
        // Check if required fields have values
        if (!roomName.trim() || !roomDesc.trim()) {
            throw new Error('Room name and description are required fields.');
        }

        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        
        if (!tenantCredentials.id || !tenantCredentials.adminSecret) {
            throw new Error('Missing tenant credentials. Please set up your PID and Secret in the credentials section.');
        }
        
        // Make API request - all progress will come from backend via SSE
        const response = await fetch('/api/kaltura/create-room-with-live', {
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
                kalturaUrl: getKalturaUrl(),
                categoryId: localStorage.getItem('publishingCategoryId') || null
            })
        });
        
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to create room');
        }

        // Clear form after successful creation
        entryNameElement.value = '';
        entryDescriptionElement.value = '';
        
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
 * Fetches and displays details for a specific session.
 * @returns {Promise<void>}
 * @throws {Error} If fetching session details fails
 */
async function handleShowEntryDetails() {
    try {
        const sessionIdElement = document.getElementById('sessionIdInput');
        
        // Check if element exists
        if (!sessionIdElement) {
            throw new Error('Session ID input element not found. Please refresh the page and try again.');
        }

        const entryId = sessionIdElement.value;
        
        // Check if required field has value
        if (!entryId.trim()) {
            throw new Error('Entry ID is required. Please enter an Entry ID.');
        }

        logMessage('Fetching details from Entry ID ' + entryId + '...');
        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        
        const response = await fetch('/api/kaltura/session-detail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                entryId, 
                partnerId: tenantCredentials.id,
                adminSecret: tenantCredentials.adminSecret,
                userId: tenantCredentials.email,
                kalturaUrl: getKalturaUrl() 
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch entry details');
        }

        const data = await response.json();
        logDataMessage(data);
    } catch (error) {
        console.error('Error fetching session details:', error);
        logMessage('Error fetching session details: ' + error.message);
        alert('Error fetching session details: ' + error.message);
    }
}



/**
 * Handles Studio mode - opens Kaltura room in new window
 * @returns {Promise<void>}
 */
async function handleStudioMode() {
    try {
        // Get all form elements with null checks
        const userIdElement = document.getElementById('userId');
        const entryIdElement = document.getElementById('entryId');
        const roleElement = document.getElementById('role');
        const firstNameElement = document.getElementById('firstName');
        const lastNameElement = document.getElementById('lastName');
        const chatModeratorElement = document.getElementById('chatModerator');
        const roomModeratorElement = document.getElementById('roomModerator');

        // Check if required elements exist
        if (!userIdElement || !entryIdElement || !roleElement) {
            throw new Error('Required form elements not found. Please refresh the page and try again.');
        }

        // Check if required fields have values
        if (!userIdElement.value.trim() || !entryIdElement.value.trim()) {
            throw new Error('userId and entryId are required fields. Please fill them in.');
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
                entryId: entryIdElement.value,
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
        logMessage('Generated Kaltura Session (Studio Mode):');
        logDataMessage(sessionData.session);

        // Build the embedded rooms URL with only the KS in the path
        const fullUrl = `https://${tenantCredentials.id}.kaf.kaltura.com/embeddedrooms/index/view-room/ks/${sessionData.session.ks}`;
        
        // Open the Kaltura room in a new window
        const newWindow = window.open(fullUrl, 'kalturaRoom', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        
        if (newWindow) {
            logMessage('Kaltura Room opened in new window');
        } else {
            logMessage('Warning: Popup blocker may have prevented the window from opening');
        }
        
        logMessage('Generated URL: ' + fullUrl);
    } catch (error) {
        console.error('Error generating session (Studio mode):', error);
        logMessage('Error generating session (Studio mode): ' + error.message);
    }
}

/**
 * Handles Player mode - loads video player in iframe
 * @returns {Promise<void>}
 */
async function handlePlayerMode() {
    try {
        // Get all form elements with null checks
        const userIdElement = document.getElementById('userId');
        const entryIdElement = document.getElementById('entryId');
        const roleElement = document.getElementById('role');
        const firstNameElement = document.getElementById('firstName');
        const lastNameElement = document.getElementById('lastName');

        // Check if required elements exist
        if (!userIdElement || !entryIdElement || !roleElement) {
            throw new Error('Required form elements not found. Please refresh the page and try again.');
        }

        // Check if required fields have values
        if (!userIdElement.value.trim() || !entryIdElement.value.trim()) {
            throw new Error('userId and entryId are required fields. Please fill them in.');
        }

        // Get tenant credentials
        const tenantCredentials = getTenantCredentials();
        console.log('Player mode - Tenant credentials:', tenantCredentials);
        
        // Generate the Kaltura session (without moderator fields for player mode)
        const sessionRequestData = {
            userId: userIdElement.value,
            entryId: entryIdElement.value,
            role: roleElement.value,
            firstName: firstNameElement ? firstNameElement.value : '',
            lastName: lastNameElement ? lastNameElement.value : '',
            chatModerator: '', // Not used in player mode
            roomModerator: '',  // Not used in player mode
            partnerId: tenantCredentials.id,
            adminSecret: tenantCredentials.adminSecret,
            kalturaUrl: getKalturaUrl()
        };
        console.log('Player mode - Session request data:', sessionRequestData);
        
        const sessionResponse = await fetch('/api/kaltura/generate-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sessionRequestData)
        });

        console.log('Player mode - Session response status:', sessionResponse.status);
        if (!sessionResponse.ok) {
            const errorData = await sessionResponse.json().catch(() => ({}));
            console.log('Player mode - Error response data:', errorData);
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
        logMessage('Generated Kaltura Session (Player Mode):');
        logDataMessage(sessionData.session);

        // Build the hosted player URL
        const playerUrl = `https://${tenantCredentials.id}.kaf.kaltura.com/hosted/index/view-entry/ks/${sessionData.session.ks}`;
        
        // Load the URL in the video player iframe
        const videoPlayerIframe = document.getElementById('videoPlayerIframe');
        if (videoPlayerIframe) {
            videoPlayerIframe.src = playerUrl;
            logMessage('Player loaded in video iframe');
        } else {
            logMessage('Error: Video player iframe not found');
        }
        
        logMessage('Generated Player URL: ' + playerUrl);
    } catch (error) {
        console.error('Error generating session (Player mode):', error);
        logMessage('Error generating session (Player mode): ' + error.message);
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

// Note: Credentials are managed through localStorage from the PID creation page
// No form fields for credentials exist on this page - they're accessed directly from localStorage

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