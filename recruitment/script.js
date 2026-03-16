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
    'Cloud Architect',
    'Other'
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
      // Ensure "Other" is always at the end
      const withOther = options.filter(o => o !== 'Other');
      withOther.push('Other');
      populateTechnologySelect(withOther);
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

function showError(fieldId, errorId, message) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  field.classList.add('invalid');
  field.classList.remove('valid');
  if (message) error.textContent = message;
  error.classList.add('show');
}

function hideError(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  field.classList.remove('invalid');
  field.classList.add('valid');
  error.classList.remove('show');
}

function clearFieldState(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  field.classList.remove('invalid', 'valid');
  error.classList.remove('show');
}

// Returns a specific error message string, or null if valid
function getNameError(value) {
  const trimmed = value.trim();
  if (!trimmed) return null; // empty — don't validate yet
  if (trimmed.length < 2) return 'Name must be at least 2 characters.';
  if (trimmed.length > 50) return 'Name must be 50 characters or fewer.';
  if (/\d/.test(trimmed)) return 'Name must not contain numbers.';
  if (!/^[a-zA-Z][a-zA-Z\s.\'\-]{1,50}$/.test(trimmed)) return 'Only letters, spaces, hyphens, apostrophes and dots are allowed.';
  if (/[\s.\'\-]{2,}/.test(trimmed)) return 'Name must not have consecutive spaces or special characters.';
  return null;
}

function getEmailError(value) {
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (!trimmed.includes('@')) return 'Email must contain @.';
  const [local, domain] = trimmed.split('@');
  if (!domain) return 'Please enter a domain after @.';
  if (!domain.includes('.')) return 'Domain must contain a dot (e.g. gmail.com).';
  if (local.startsWith('.') || local.endsWith('.')) return 'Local part must not start or end with a dot.';
  if (!/^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(trimmed)) return 'Enter a valid email address.';
  return null;
}

function getMobileError(value) {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const cleaned = trimmed.replace(/[\s\-\(\)]/g, '');
  if (!/^(\+91|91|0)?[0-9]+$/.test(cleaned)) return 'Only digits, +, spaces, and hyphens are allowed.';
  if (!/^(\+91|91|0)?[6-9]\d{9}$/.test(cleaned)) return 'Must be a valid Indian mobile number starting with 6–9 (10 digits).';
  return null;
}

function getDobError(value) {
  if (!value) return null;
  const date = new Date(value);
  const today = new Date();
  const minAge = new Date(today.getFullYear() - 100, today.getMonth(), today.getDate());
  const maxAge = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate());
  if (date > maxAge) return 'Candidate must be at least 16 years old.';
  if (date < minAge) return 'Please enter a valid date of birth.';
  return null;
}

function getYoeError(value) {
  const trimmed = value.trim();
  if (trimmed === '') return null;
  const num = Number(trimmed);
  if (!Number.isInteger(num) || num < 0 || num > 50) return 'Year of experience must be a whole number between 0 and 50.';
  return null;
}

function getPreferredLocationError(value) {
  const trimmed = value.trim();
  if (trimmed === '') return null;
  // Split by comma and validate each entry
  const parts = trimmed.split(',').map(p => p.trim());
  if (parts.some(p => p === '')) return 'Please separate locations with a comma, e.g. Bangalore, Chennai.';
  if (parts.some(p => p.length < 2)) return 'Each location must be at least 2 characters.';
  if (trimmed.length > 200) return 'Locations must be 200 characters or fewer.';
  return null;
}

// Validate and update UI for a field; returns true if valid
function validateField(fieldId, errorId, getErrorFn) {
  const field = document.getElementById(fieldId);
  const value = field.value;
  if (!value.trim()) {
    clearFieldState(fieldId, errorId);
    return false; // empty, not valid
  }
  const msg = getErrorFn(value);
  if (msg) {
    showError(fieldId, errorId, msg);
    return false;
  } else {
    hideError(fieldId, errorId);
    return true;
  }
}

// Real-time + blur validation
function setupValidation() {
  const firstName = document.getElementById('firstName');
  const lastName = document.getElementById('lastName');
  const email = document.getElementById('email');
  const mobile = document.getElementById('mobile');
  const dob = document.getElementById('dob');
  const technology = document.getElementById('technology');
  const yoe = document.getElementById('yoe');
  const preferredLocation = document.getElementById('preferredLocation');

  function addListeners(el, fieldId, errorId, getErrorFn) {
    // On input: validate only if the field already has been touched
    el.addEventListener('input', () => {
      if (el.dataset.touched) validateField(fieldId, errorId, getErrorFn);
    });
    // On blur: mark as touched and always validate
    el.addEventListener('blur', () => {
      if (el.value.trim()) {
        el.dataset.touched = '1';
        validateField(fieldId, errorId, getErrorFn);
      }
    });
  }

  addListeners(firstName, 'firstName', 'firstNameError', getNameError);
  addListeners(lastName, 'lastName', 'lastNameError', getNameError);
  addListeners(email, 'email', 'emailError', getEmailError);
  addListeners(mobile, 'mobile', 'mobileError', getMobileError);
  addListeners(yoe, 'yoe', 'yoeError', getYoeError);

  // Preferred Location: validate on every input (not just after first blur)
  const prefLocEl = document.getElementById('preferredLocation');
  prefLocEl.addEventListener('input', () => {
    prefLocEl.dataset.touched = '1';
    validateField('preferredLocation', 'preferredLocationError', getPreferredLocationError);
  });
  prefLocEl.addEventListener('blur', () => {
    prefLocEl.dataset.touched = '1';
    validateField('preferredLocation', 'preferredLocationError', getPreferredLocationError);
  });

  // DOB: validate on change (date picker fires change, not input)
  dob.addEventListener('change', () => {
    dob.dataset.touched = '1';
    validateField('dob', 'dobError', getDobError);
  });
  dob.addEventListener('blur', () => {
    if (dob.value) {
      dob.dataset.touched = '1';
      validateField('dob', 'dobError', getDobError);
    }
  });

  technology.addEventListener('change', () => {
    if (technology.value) {
      hideError('technology', 'technologyError');
    }
  });
}

// Show/hide "Other" text box based on dropdown selection
function setupOtherTechnology() {
  const technology = document.getElementById('technology');
  const wrapper = document.getElementById('otherTechWrapper');
  const otherInput = document.getElementById('otherTechnology');

  technology.addEventListener('change', () => {
    if (technology.value === 'Other') {
      wrapper.classList.add('visible');
      otherInput.required = true;
      // Trigger validation once touched
      otherInput.addEventListener('input', function onInput() {
        if (otherInput.value.trim().length >= 2) {
          hideError('otherTechnology', 'otherTechnologyError');
        }
      });
    } else {
      wrapper.classList.remove('visible');
      otherInput.required = false;
      otherInput.value = '';
      clearFieldState('otherTechnology', 'otherTechnologyError');
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
  const otherTechnology = document.getElementById('otherTechnology').value.trim();
  const yoe = document.getElementById('yoe').value.trim();
  const preferredLocation = document.getElementById('preferredLocation').value.trim();
  const linkedinCompany = document.getElementById('linkedinCompany').checked;
  const linkedinProfile = document.getElementById('linkedinProfile').checked;

  // Validate all fields using specific error functions
  let isValid = true;

  const fnErr = getNameError(firstName);
  if (!firstName || fnErr) {
    showError('firstName', 'firstNameError', fnErr || 'First name is required.');
    isValid = false;
  } else {
    hideError('firstName', 'firstNameError');
  }

  const lnErr = getNameError(lastName);
  if (!lastName || lnErr) {
    showError('lastName', 'lastNameError', lnErr || 'Last name is required.');
    isValid = false;
  } else {
    hideError('lastName', 'lastNameError');
  }

  const emailErr = getEmailError(email);
  if (!email || emailErr) {
    showError('email', 'emailError', emailErr || 'Email address is required.');
    isValid = false;
  } else {
    hideError('email', 'emailError');
  }

  const dobErr = getDobError(dob);
  if (!dob || dobErr) {
    showError('dob', 'dobError', dobErr || 'Date of birth is required.');
    isValid = false;
  } else {
    hideError('dob', 'dobError');
  }

  const mobileErr = getMobileError(mobile);
  if (!mobile || mobileErr) {
    showError('mobile', 'mobileError', mobileErr || 'Mobile number is required.');
    isValid = false;
  } else {
    hideError('mobile', 'mobileError');
  }

  if (!technology) {
    showError('technology', 'technologyError', 'Please select a technology/role.');
    isValid = false;
  } else {
    hideError('technology', 'technologyError');
  }

  // Validate custom tech input when Other is selected
  if (technology === 'Other') {
    if (!otherTechnology || otherTechnology.length < 2) {
      showError('otherTechnology', 'otherTechnologyError', 'Please describe your technology/role (at least 2 characters).');
      isValid = false;
    } else {
      hideError('otherTechnology', 'otherTechnologyError');
    }
  }

  const yoeErr = getYoeError(yoe);
  if (yoe === '' || yoeErr) {
    showError('yoe', 'yoeError', yoeErr || 'Year of experience is required.');
    isValid = false;
  } else {
    hideError('yoe', 'yoeError');
  }

  const locErr = getPreferredLocationError(preferredLocation);
  if (!preferredLocation || locErr) {
    showError('preferredLocation', 'preferredLocationError', locErr || 'Preferred location is required.');
    isValid = false;
  } else {
    hideError('preferredLocation', 'preferredLocationError');
  }

  if (!isValid) {
    showStatus('Please fix the errors before submitting.', 'error');
    return;
  }

  // Show loading state
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.classList.add('loading');
  submitBtn.disabled = true;

  // Prepare form data — use typed value when Other is selected
  const finalTechnology = technology === 'Other' ? `Other: ${otherTechnology}` : technology;
  const formData = {
    firstName,
    lastName,
    email,
    dob,
    mobile,
    technology: finalTechnology,
    yoe,
    preferredLocation,
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

      // Hide Other tech field and reset touched states
      document.getElementById('otherTechWrapper').classList.remove('visible');
      document.querySelectorAll('.form-control[data-touched]').forEach(f => delete f.dataset.touched);

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
  setupOtherTechnology();
  setupClickableCheckboxes();
  setupProgressTracking();

  const form = document.getElementById('referralForm');
  form.addEventListener('submit', handleFormSubmit);
});
