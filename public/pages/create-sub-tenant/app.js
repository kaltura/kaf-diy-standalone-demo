// Simplified developer-only script for sub-tenant creation
// No credentials are collected in the browser; the backend relies on environment variables.
window.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('createTenant');
  if (btn) {
    btn.addEventListener('click', createSubTenant);
  }
});

async function createSubTenant() {
  const resultEl = document.getElementById('result');
  resultEl.style.display = 'block';
  resultEl.textContent = 'Initializing request...';

  try {
    // Create sub-tenant and publishing category in one call
    const { response, body } = await fetchHelper(
      window.location.origin + '/api/kaltura/create-sub-tenant',
      'POST',
      JSON.stringify({})
    );

    if (response.status === 200 && body.success) {
      resultEl.className = 'result success';
      
      // Save tenant credentials to localStorage for use by other pages
      const tenant = body.result;
      if (tenant && tenant.id && tenant.email && tenant.adminSecret) {
        localStorage.setItem('tenantId', tenant.id);
        localStorage.setItem('tenantEmail', tenant.email);
        localStorage.setItem('adminSecret', tenant.adminSecret);
        localStorage.setItem('kalturaUrl', 'https://www.kaltura.com');
      }

      // Save category ID to localStorage
      const category = body.category;
      if (category && category.id) {
        localStorage.setItem('publishingCategoryId', category.id);
      }

      resultEl.textContent = 'Sub-tenant and publishing category created successfully:\n\n' +
        JSON.stringify({ tenant, category }, null, 2);
    } else {
      throw new Error(body.message || 'Failed to create sub-tenant and category');
    }
  } catch (err) {
    resultEl.className = 'result error';
    resultEl.textContent = 'Error: ' + err.message;
  }
} 