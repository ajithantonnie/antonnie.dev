// Configuration - Google Sheets Integration
const GOOGLE_SHEETS_CONFIG = {
  // Replace with your Google Apps Script Web App URL
  // Instructions in README.md on how to set this up
  scriptUrl: 'https://script.google.com/macros/s/AKfycbx6q30kQF_WVIpaDuzPNWnmUPplZKECmZUVD-6e1nGLk2EvIjaLFvrgKW3jbpq-_hOU/exec',

  // Fallback technology options if Google Sheets is not configured
  fallbackTechnologyOptions: [
    'Java Backend',
    'Java Fullstack',
    'UI/UX Designer',
    'Frontend Developer',
    'Python Developer',
    'DevOps Engineer',
    'Data Scientist',
    'Mobile App Developer',
    'QA Engineer',
    'Cloud Architect'
  ]
};

// Populate dropdown with a given list of options
function populateTechnologySelect(options) {
  const technologySelect = document.getElementById('technology');
  const currentValue = technologySelect.value;
  technologySelect.innerHTML = '<option value="">-- Select Technology/Role --</option>';
  options.forEach(option => {
    const optionElement = document.createElement('option');
    optionElement.value = option;
    optionElement.textContent = option;
    technologySelect.appendChild(optionElement);
  });
  if (currentValue && options.includes(currentValue)) {
    technologySelect.value = currentValue;
  }
  technologySelect.disabled = false;
}

// Load technology options from Google Sheets
async function loadTechnologyOptions() {
  const technologySelect = document.getElementById('technology');

  // Show loading state — dropdown is disabled until data arrives
  technologySelect.innerHTML = '<option value="">Loading options...</option>';
  technologySelect.disabled = true;

  try {
    const response = await fetch(`${GOOGLE_SHEETS_CONFIG.scriptUrl}?action=getTechnologyOptions`);

    if (!response.ok) {
      throw new Error('Failed to fetch from Google Sheets');
    }

    const data = await response.json();
    const options = data.technologyOptions;

    if (options && options.length > 0) {
      populateTechnologySelect(options);
    } else {
      // Empty list from Sheets — fall back silently
      populateTechnologySelect(GOOGLE_SHEETS_CONFIG.fallbackTechnologyOptions);
    }
  } catch (error) {
    // Network/script error — fall back silently
    console.warn('Could not load options from Google Sheets, using fallback:', error.message);
    populateTechnologySelect(GOOGLE_SHEETS_CONFIG.fallbackTechnologyOptions);
  }
}

// Form validation functions
function validateName(name) {
  // Must be at least 2 characters, only letters, spaces, hyphens, apostrophes, and dots
  // No numbers or special characters except . - '
  const nameRegex = /^[a-zA-Z][a-zA-Z\s.'-]{1,50}$/;
  const trimmedName = name.trim();

  if (trimmedName.length < 2 || trimmedName.length > 50) {
    return false;
  }

  if (!nameRegex.test(trimmedName)) {
    return false;
  }

  // Check for consecutive spaces or special characters
  if (/[\s.'-]{2,}/.test(trimmedName)) {
    return false;
  }

  return true;
}

function validateEmail(email) {
  // Comprehensive email validation
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const trimmedEmail = email.trim().toLowerCase();

  if (!emailRegex.test(trimmedEmail)) {
    return false;
  }

  // Additional checks
  const parts = trimmedEmail.split('@');
  if (parts.length !== 2) return false;

  const [localPart, domain] = parts;

  // Local part should not start or end with a dot
  if (localPart.startsWith('.') || localPart.endsWith('.')) {
    return false;
  }

  // Domain should have at least one dot
  if (!domain.includes('.')) {
    return false;
  }

  return true;
}

function validateIndianMobile(mobile) {
  // Indian mobile number validation
  // Accepts formats:
  // - 9876543210
  // - +919876543210
  // - 09876543210
  // - +91 9876543210
  // - +91-9876543210
  // - 91 9876543210
  // - (91) 9876543210

  // Remove all spaces, hyphens, parentheses
  const cleaned = mobile.replace(/[\s\-\(\)]/g, '');

  // Check if it matches Indian mobile pattern
  // Indian mobile numbers start with 6, 7, 8, or 9 and are 10 digits long
  const indianMobileRegex = /^(\+91|91|0)?[6-9]\d{9}$/;

  if (!indianMobileRegex.test(cleaned)) {
    return false;
  }

  // Extract just the 10-digit number
  let digits = cleaned;
  if (cleaned.startsWith('+91')) {
    digits = cleaned.substring(3);
  } else if (cleaned.startsWith('91') && cleaned.length === 12) {
    digits = cleaned.substring(2);
  } else if (cleaned.startsWith('0') && cleaned.length === 11) {
    digits = cleaned.substring(1);
  }

  // Verify it's exactly 10 digits starting with 6-9
  return /^[6-9]\d{9}$/.test(digits);
}

function validateDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const minAge = new Date(today.getFullYear() - 100, today.getMonth(), today.getDate());
  const maxAge = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate());

  return date >= minAge && date <= maxAge;
}

function showError(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  field.classList.add('invalid');
  field.classList.remove('valid');
  error.classList.add('show');
}

function hideError(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  field.classList.remove('invalid');
  field.classList.add('valid');
  error.classList.remove('show');
}

// Real-time validation
function setupValidation() {
  const firstName = document.getElementById('firstName');
  const lastName = document.getElementById('lastName');
  const email = document.getElementById('email');
  const mobile = document.getElementById('mobile');
  const dob = document.getElementById('dob');
  const technology = document.getElementById('technology');

  firstName.addEventListener('blur', () => {
    if (firstName.value && !validateName(firstName.value)) {
      showError('firstName', 'firstNameError');
    } else if (firstName.value) {
      hideError('firstName', 'firstNameError');
    }
  });

  lastName.addEventListener('blur', () => {
    if (lastName.value && !validateName(lastName.value)) {
      showError('lastName', 'lastNameError');
    } else if (lastName.value) {
      hideError('lastName', 'lastNameError');
    }
  });

  email.addEventListener('blur', () => {
    if (email.value && !validateEmail(email.value)) {
      showError('email', 'emailError');
    } else if (email.value) {
      hideError('email', 'emailError');
    }
  });

  mobile.addEventListener('blur', () => {
    if (mobile.value && !validateIndianMobile(mobile.value)) {
      showError('mobile', 'mobileError');
    } else if (mobile.value) {
      hideError('mobile', 'mobileError');
    }
  });

  dob.addEventListener('blur', () => {
    if (dob.value && !validateDate(dob.value)) {
      showError('dob', 'dobError');
    } else if (dob.value) {
      hideError('dob', 'dobError');
    }
  });

  technology.addEventListener('change', () => {
    if (technology.value) {
      hideError('technology', 'technologyError');
    }
  });
}

// Submit form to Google Sheets
async function submitToGoogleSheets(formData) {
  try {
    const response = await fetch(GOOGLE_SHEETS_CONFIG.scriptUrl, {
      method: 'POST',
      mode: 'no-cors', // Use no-cors to avoid CORS issues
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'submitReferral',
        data: formData
      })
    });

    // With no-cors mode, we can't read the response, but the request will be sent
    return { success: true };
  } catch (error) {
    console.error('Error submitting to Google Sheets:', error);
    return { success: false, error: error.message };
  }
}

// Handle form submission
function handleFormSubmit(event) {
  event.preventDefault();

  // Get form values
  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const email = document.getElementById('email').value.trim();
  const dob = document.getElementById('dob').value;
  const mobile = document.getElementById('mobile').value.trim();
  const technology = document.getElementById('technology').value;
  const linkedinCompany = document.getElementById('linkedinCompany').checked;
  const linkedinProfile = document.getElementById('linkedinProfile').checked;

  // Validate all fields
  let isValid = true;

  if (!validateName(firstName)) {
    showError('firstName', 'firstNameError');
    isValid = false;
  } else {
    hideError('firstName', 'firstNameError');
  }

  if (!validateName(lastName)) {
    showError('lastName', 'lastNameError');
    isValid = false;
  } else {
    hideError('lastName', 'lastNameError');
  }

  if (!validateEmail(email)) {
    showError('email', 'emailError');
    isValid = false;
  } else {
    hideError('email', 'emailError');
  }

  if (!validateDate(dob)) {
    showError('dob', 'dobError');
    isValid = false;
  } else {
    hideError('dob', 'dobError');
  }

  if (!validateIndianMobile(mobile)) {
    showError('mobile', 'mobileError');
    isValid = false;
  } else {
    hideError('mobile', 'mobileError');
  }

  if (!technology) {
    showError('technology', 'technologyError');
    isValid = false;
  } else {
    hideError('technology', 'technologyError');
  }

  if (!isValid) {
    showStatus('Please fix the errors before submitting.', 'error');
    return;
  }

  // Show loading state
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.classList.add('loading');
  submitBtn.disabled = true;

  // Prepare form data
  const formData = {
    firstName,
    lastName,
    email,
    dob,
    mobile,
    technology,
    linkedinCompany: linkedinCompany ? 'Yes' : 'No',
    linkedinProfile: linkedinProfile ? 'Yes' : 'No',
    timestamp: new Date().toISOString()
  };

  // Submit to Google Sheets
  submitToGoogleSheets(formData)
    .then(result => {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;

      showStatus('✓ Referral submitted successfully! Thank you for your submission.', 'success');
      document.getElementById('referralForm').reset();

      // Remove all validation classes
      document.querySelectorAll('.form-control').forEach(field => {
        field.classList.remove('valid', 'invalid');
      });

      // Remove checked state from checkboxes
      document.querySelectorAll('.checkbox-group').forEach(group => {
        group.classList.remove('checked');
      });

      // Scroll to success message
      setTimeout(() => {
        document.getElementById('statusMessage').scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }, 100);
    })
    .catch(error => {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      showStatus('An error occurred. Please try again later.', 'error');
      console.error('Submission error:', error);
    });
}

// Show status message
function showStatus(message, type) {
  const statusMessage = document.getElementById('statusMessage');
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${type}`;

  if (type === 'success') {
    setTimeout(() => {
      statusMessage.style.display = 'none';
    }, 5000);
  }
}

// Setup clickable checkboxes
function setupClickableCheckboxes() {
  const checkboxGroups = document.querySelectorAll('.checkbox-group');

  checkboxGroups.forEach(group => {
    const checkbox = group.querySelector('input[type="checkbox"]');

    // Toggle checkbox when clicking anywhere on the group (except links)
    group.addEventListener('click', (e) => {
      // Don't toggle if clicking on a link
      if (e.target.tagName === 'A') {
        return;
      }

      // Don't toggle if clicking directly on the checkbox (it will toggle itself)
      if (e.target === checkbox) {
        return;
      }

      checkbox.checked = !checkbox.checked;

      // Trigger change event
      checkbox.dispatchEvent(new Event('change'));
    });

    // Add visual feedback when checkbox state changes
    checkbox.addEventListener('change', () => {
      if (checkbox.checked) {
        group.classList.add('checked');
      } else {
        group.classList.remove('checked');
      }
    });
  });
}

// Update progress steps based on form completion
function updateProgressSteps() {
  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const email = document.getElementById('email').value.trim();
  const dob = document.getElementById('dob').value;
  const mobile = document.getElementById('mobile').value.trim();
  const technology = document.getElementById('technology').value;

  const steps = document.querySelectorAll('.step');

  // Step 1: Personal Info (First Name, Last Name)
  if (firstName && lastName) {
    steps[0].classList.add('completed');
    steps[1].classList.add('active');
  } else {
    steps[0].classList.remove('completed');
    steps[1].classList.remove('active');
  }

  // Step 2: Contact (Email, DOB, Mobile)
  if (email && dob && mobile) {
    steps[1].classList.add('completed');
    steps[2].classList.add('active');
  } else {
    steps[1].classList.remove('completed');
    steps[2].classList.remove('active');
  }

  // Step 3: Role (Technology)
  if (technology) {
    steps[2].classList.add('completed');
    steps[3].classList.add('active');
  } else {
    steps[2].classList.remove('completed');
    steps[3].classList.remove('active');
  }
}

// Setup progress tracking
function setupProgressTracking() {
  const formFields = document.querySelectorAll('.form-control');
  formFields.forEach(field => {
    field.addEventListener('input', updateProgressSteps);
    field.addEventListener('change', updateProgressSteps);
  });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  loadTechnologyOptions();
  setupValidation();
  setupClickableCheckboxes();
  setupProgressTracking();

  const form = document.getElementById('referralForm');
  form.addEventListener('submit', handleFormSubmit);
});
