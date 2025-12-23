// Global state
let allRealms = [];
let allObjects = {};
let currentRealm = null;
let currentObject = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing wiki editor...');
    await loadRealms();
    attachEventListeners();
});

// Load all realms
async function loadRealms() {
    try {
        const response = await fetch('/api/realms');
        allRealms = await response.json();
        console.log('Loaded realms:', allRealms);
        
        const realmSelect = document.getElementById('realm');
        if (realmSelect) {
            allRealms.forEach(realm => {
                const option = document.createElement('option');
                option.value = realm;
                option.textContent = realm;
                realmSelect.appendChild(option);
            });
        }
    } catch (error) {
        showMessage('Failed to load realms: ' + error.message, 'error');
    }
}

// Load objects for selected realm
async function loadObjects() {
    const realmSelect = document.getElementById('realm');
    const realm = realmSelect.value;
    
    if (!realm) {
        document.getElementById('object').innerHTML = '<option value="">Select a realm first...</option>';
        document.getElementById('objectSearch').value = '';
        return;
    }
    
    currentRealm = realm;
    
    try {
        const response = await fetch(`/api/realm/${encodeURIComponent(realm)}/objects`);
        const data = await response.json();
        
        // Check if response is an error object
        if (data.error || !Array.isArray(data)) {
            showMessage(`Failed to load objects: ${data.error || 'Invalid response'}`, 'error');
            document.getElementById('object').innerHTML = '<option value="">Error loading objects</option>';
            return;
        }
        
        allObjects[realm] = data;
        console.log(`Loaded ${data.length} objects for realm: ${realm}`);
        
        updateObjectSelect(data);
    } catch (error) {
        showMessage(`Failed to load objects: ${error.message}`, 'error');
        console.error('Error details:', error);
    }
}

// Update object select dropdown
function updateObjectSelect(objects) {
    const objectSelect = document.getElementById('object');
    objectSelect.innerHTML = '<option value="">Select an object...</option>';
    
    objects.forEach(obj => {
        const option = document.createElement('option');
        option.value = obj.id;
        option.textContent = obj.name;
        objectSelect.appendChild(option);
    });
}

// Handle object search with fuzzy matching
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('objectSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        const objectSelect = document.getElementById('object');
        
        if (!currentRealm || !allObjects[currentRealm]) return;
        
        const objects = allObjects[currentRealm];
        
        if (!query) {
            // No search query, show all objects
            updateObjectSelect(objects);
            return;
        }
        
        // Filter objects by name (fuzzy-like matching)
        const filtered = objects.filter(obj => {
            const name = obj.name.toLowerCase();
            // Check if name contains the query or starts with it
            return name.includes(query) || name.startsWith(query);
        });
        
        // Sort: exact matches first, then contains matches
        filtered.sort((a, b) => {
            const aExact = a.name.toLowerCase() === query ? 1 : 0;
            const bExact = b.name.toLowerCase() === query ? 1 : 0;
            return bExact - aExact;
        });
        
        updateObjectSelect(filtered);
    });
});

// Load selected object details
async function loadObject() {
    const objectSelect = document.getElementById('object');
    const objectId = objectSelect.value;
    
    if (!objectId || !currentRealm) {
        clearForm();
        document.getElementById('preview').innerHTML = '<p style="color: #999;">Select an object to see preview</p>';
        return;
    }
    
    try {
        const response = await fetch(`/api/object/${encodeURIComponent(currentRealm)}/${objectId}`);
        const data = await response.json();
        
        // Check if response is an error
        if (data.error) {
            showMessage(`Failed to load object: ${data.error}`, 'error');
            clearForm();
            return;
        }
        
        currentObject = data;
        console.log('Loaded object:', data);
        
        // Populate form fields
        document.getElementById('objectName').value = data.name || '';
        document.getElementById('difficulty').value = data.difficulty || 'Common';
        document.getElementById('area').value = data.area || '';
        document.getElementById('hint').value = data.hint || '';
        document.getElementById('info').value = data.description || '';
        document.getElementById('obtaining').value = data.obtaining || '';
        document.getElementById('image').value = data.image || '';
        document.getElementById('oldImage').value = data.old_image || '';
        document.getElementById('previousDifficulties').value = data.previous_difficulties || '';
        
        // Auto-generate preview
        await generateMarkup();
    } catch (error) {
        showMessage(`Failed to load object: ${error.message}`, 'error');
        console.error('Error details:', error);
    }
}

// Clear form fields
function clearForm() {
    document.getElementById('objectName').value = '';
    document.getElementById('difficulty').value = 'Common';
    document.getElementById('area').value = '';
    document.getElementById('hint').value = '';
    document.getElementById('info').value = '';
    document.getElementById('obtaining').value = '';
    document.getElementById('image').value = '';
    document.getElementById('oldImage').value = '';
    document.getElementById('previousDifficulties').value = '';
}

// Generate wiki markup preview
async function generateMarkup() {
    if (!currentRealm) {
        showMessage('Please select a realm first', 'error');
        return;
    }
    
    const formData = {
        realm: currentRealm,
        name: document.getElementById('objectName').value || (currentObject ? currentObject.name : ''),
        difficulty: document.getElementById('difficulty').value,
        area: document.getElementById('area').value,
        hint: document.getElementById('hint').value,
        info: document.getElementById('info').value,
        obtaining: document.getElementById('obtaining').value,
        image: document.getElementById('image').value,
        old_image: document.getElementById('oldImage').value,
        previous_difficulties: document.getElementById('previousDifficulties').value,
        id: currentObject ? currentObject.id : ''
    };
    
    try {
        const response = await fetch('/api/generate-markup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            showMessage(`Failed to generate markup: ${result.error}`, 'error');
            return;
        }
        
        if (result.markup) {
            const preview = document.getElementById('preview');
            preview.textContent = result.markup;  // Use textContent for code display
            preview.classList.add('wiki-markup');
            showMessage('Preview generated successfully', 'success');
        } else {
            showMessage('No markup generated', 'error');
        }
    } catch (error) {
        showMessage(`Error generating preview: ${error.message}`, 'error');
        console.error('Error details:', error);
    }
}

// Save page locally
async function savePage() {
    if (!currentRealm) {
        showMessage('Please select a realm first', 'error');
        return;
    }
    
    const formData = {
        realm: currentRealm,
        name: document.getElementById('objectName').value || (currentObject ? currentObject.name : ''),
        difficulty: document.getElementById('difficulty').value,
        area: document.getElementById('area').value,
        hint: document.getElementById('hint').value,
        info: document.getElementById('info').value,
        obtaining: document.getElementById('obtaining').value,
        image: document.getElementById('image').value,
        old_image: document.getElementById('oldImage').value,
        previous_difficulties: document.getElementById('previousDifficulties').value,
        id: currentObject ? currentObject.id : ''
    };
    
    try {
        const response = await fetch('/api/save-page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage(`Page saved to ${result.filepath}`, 'success');
        } else {
            showMessage(`Failed to save page: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage(`Error saving page: ${error.message}`, 'error');
    }
}

// Copy markup to clipboard
function copyMarkup() {
    const preview = document.getElementById('preview');
    const text = preview.innerText;
    
    if (!text || text.includes('Select an object')) {
        showMessage('Nothing to copy. Generate a preview first.', 'info');
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        showMessage('Markup copied to clipboard!', 'success');
    }).catch(err => {
        showMessage('Failed to copy: ' + err.message, 'error');
    });
}

// Download markup as text file
function downloadMarkup() {
    const preview = document.getElementById('preview');
    const text = preview.innerText;
    
    if (!text || text.includes('Select an object')) {
        showMessage('Nothing to download. Generate a preview first.', 'info');
        return;
    }
    
    const element = document.createElement('a');
    const objectName = document.getElementById('objectName').value || 'object';
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', `${objectName}_markup.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    showMessage('Markup downloaded!', 'success');
}

// Publish to wiki (placeholder - requires authentication)
async function publishToWiki() {
    showMessage('Wiki publishing coming soon! For now, use the CLI tool or copy markup manually.', 'info');
    // TODO: Implement wiki publishing after authentication setup
}

// Show status message
function showMessage(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    if (!statusDiv) return;
    
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type} show`;
    
    setTimeout(() => {
        statusDiv.classList.remove('show');
    }, 5000);
}

// Attach event listeners
function attachEventListeners() {
    const realmSelect = document.getElementById('realm');
    const objectSelect = document.getElementById('object');
    const previewBtn = document.querySelector('button[onclick*="generateMarkup"]');
    const saveBtn = document.querySelector('button[onclick*="savePage"]');
    const publishBtn = document.querySelector('button[onclick*="publishToWiki"]');
    
    if (realmSelect) realmSelect.addEventListener('change', loadObjects);
    if (objectSelect) objectSelect.addEventListener('change', loadObject);
}

// Escape HTML for display in preview
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-save to localStorage (draft functionality)
function autoSaveDraft() {
    const formData = {
        realm: document.getElementById('realm')?.value,
        name: document.getElementById('objectName')?.value,
        difficulty: document.getElementById('difficulty')?.value,
        area: document.getElementById('area')?.value,
        hint: document.getElementById('hint')?.value,
        info: document.getElementById('info')?.value,
        obtaining: document.getElementById('obtaining')?.value,
        image: document.getElementById('image')?.value,
        oldImage: document.getElementById('oldImage')?.value,
        previousDifficulties: document.getElementById('previousDifficulties')?.value
    };
    
    localStorage.setItem('ftbc_wiki_draft', JSON.stringify(formData));
}

// Load draft from localStorage
function loadDraft() {
    const draft = localStorage.getItem('ftbc_wiki_draft');
    if (!draft) return;
    
    const data = JSON.parse(draft);
    
    if (data.realm) document.getElementById('realm').value = data.realm;
    if (data.name) document.getElementById('objectName').value = data.name;
    if (data.difficulty) document.getElementById('difficulty').value = data.difficulty;
    if (data.area) document.getElementById('area').value = data.area;
    if (data.hint) document.getElementById('hint').value = data.hint;
    if (data.info) document.getElementById('info').value = data.info;
    if (data.obtaining) document.getElementById('obtaining').value = data.obtaining;
    if (data.image) document.getElementById('image').value = data.image;
    if (data.oldImage) document.getElementById('oldImage').value = data.oldImage;
    if (data.previousDifficulties) document.getElementById('previousDifficulties').value = data.previousDifficulties;
    
    showMessage('Draft loaded from localStorage', 'info');
}

// Set up auto-save every 30 seconds
setInterval(autoSaveDraft, 30000);

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        savePage();
    }
    
    // Ctrl+P or Cmd+P to preview
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        generateMarkup();
    }
});

// Initialize loading animations
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = '<span class="spinner"></span> Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || 'Load';
    }
}
