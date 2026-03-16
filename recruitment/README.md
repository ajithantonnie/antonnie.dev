# Recruitment Referral Page

A modern, responsive recruitment referral form with Google Sheets integration for dynamic configuration and data storage.

## Features

- ✨ **Modern UI Design** with floating animations and gradient backgrounds
- 📱 **Fully Responsive** (mobile, tablet, desktop)
- ✅ **Advanced Form Validation**
  - Indian mobile number validation (+91, 10 digits starting with 6-9)
  - Email validation with comprehensive checks
  - Name validation (2-50 characters, letters only)
  - Age validation (16-100 years)
- 🔧 **Google Sheets Integration**
  - Dynamic technology options loaded from Google Sheets
  - Form submissions stored in Google Sheets
  - Easy to update options without code changes
- 🔗 **Optional LinkedIn Checkboxes** (fully clickable)
- ♿ **Accessible and User-Friendly**
- 🎨 **Beautiful Design Elements**
  - Floating decorative icons
  - Info cards with hover effects
  - Smooth animations
  - Glassmorphism effects

## Files

- **index.html** - Main recruitment page with enhanced UI
- **script.js** - Form validation, Google Sheets integration, and submission logic
- **README.md** - This file

## Google Sheets Integration Setup

### Why Google Sheets?

Instead of using a static `config.json` file, this form uses Google Sheets to:
1. **Dynamically load technology options** - Update the dropdown options anytime by editing a Google Sheet
2. **Store form submissions** - All referrals are automatically saved to a Google Sheet
3. **Easy management** - No need to redeploy or edit code files

### Step-by-Step Setup

#### 1. Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Recruitment Referrals"

#### 2. Set Up Two Sheets

**Sheet 1: "Submissions"** (for storing form data)
- Create headers in Row 1:
  - A1: `Timestamp`
  - B1: `First Name`
  - C1: `Last Name`
  - D1: `Email`
  - E1: `Date of Birth`
  - F1: `Mobile Number`
  - G1: `Technology/Role`
  - H1: `LinkedIn Company`
  - I1: `LinkedIn Profile`
  - J1: `YOE`

**Sheet 2: "TechnologyOptions"** (for dropdown options)
- Create a header in A1: `Technology Options`
- Add your technology options starting from A2:
  - A2: `Java Backend`
  - A3: `Java Fullstack`
  - A4: `UI/UX Designer`
  - A5: `Frontend Developer`
  - A6: `Python Developer`
  - A7: `DevOps Engineer`
  - (Add as many as you need)

#### 3. Create Google Apps Script

1. In your Google Sheet, click **Extensions** → **Apps Script**
2. Delete any existing code
3. Paste the following code:

```javascript
// Google Apps Script for Recruitment Form

function doGet(e) {
  const action = e.parameter.action;
  
  if (action === 'getTechnologyOptions') {
    return getTechnologyOptions();
  }
  
  return ContentService.createTextOutput(JSON.stringify({
    error: 'Invalid action'
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    if (data.action === 'submitReferral') {
      return submitReferral(data.data);
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Invalid action'
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function getTechnologyOptions() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('TechnologyOptions');
  
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({
      technologyOptions: ['Java Backend', 'Java Fullstack', 'UI/UX Designer']
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  // Get all values from column A (starting from row 2)
  const lastRow = sheet.getLastRow();
  const options = [];
  
  if (lastRow > 1) {
    const values = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
    values.forEach(row => {
      if (row[0] && row[0].toString().trim() !== '') {
        options.push(row[0].toString().trim());
      }
    });
  }
  
  return ContentService.createTextOutput(JSON.stringify({
    technologyOptions: options
  })).setMimeType(ContentService.MimeType.JSON);
}

function submitReferral(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Submissions');
  
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Submissions sheet not found'
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  // Append the data to the sheet
  sheet.appendRow([
    data.timestamp || new Date().toISOString(),
    data.firstName,
    data.lastName,
    data.email,
    data.dob,
    data.mobile,
    data.technology,
    data.linkedinCompany,
    data.linkedinProfile,
    data.yoe
  ]);
  
  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    message: 'Referral submitted successfully'
  })).setMimeType(ContentService.MimeType.JSON);
}
```

4. Click **Save** (💾 icon)
5. Name your project: "Recruitment Form Handler"

#### 4. Deploy the Apps Script

1. Click **Deploy** → **New deployment**
2. Click the gear icon ⚙️ next to "Select type"
3. Choose **Web app**
4. Configure:
   - **Description**: "Recruitment Form API"
   - **Execute as**: Me
   - **Who has access**: Anyone
5. Click **Deploy**
6. **Authorize** the script (you may need to click "Advanced" → "Go to [Project Name]")
7. **Copy the Web App URL** (it looks like: `https://script.google.com/macros/s/AKfycby.../exec`)

#### 5. Update Your Website Code

1. Open `script.js` in your recruitment folder
2. Find line 2-4 (the `GOOGLE_SHEETS_CONFIG` section)
3. Replace `YOUR_SCRIPT_ID` with your actual Web App URL:

```javascript
const GOOGLE_SHEETS_CONFIG = {
  scriptUrl: 'https://script.google.com/macros/s/AKfycby_YOUR_ACTUAL_URL/exec',
  // ... rest of config
};
```

4. Save the file

### Testing the Integration

1. Open your recruitment page
2. The technology dropdown should load options from your Google Sheet
3. Fill out and submit the form
4. Check your Google Sheet's "Submissions" tab - you should see the new entry!

### Updating Technology Options

Simply edit the "TechnologyOptions" sheet in your Google Spreadsheet:
- Add new rows for new options
- Delete rows to remove options
- Edit existing rows to change option names
- Changes will appear on the website immediately (no code changes needed!)

## Form Validation Details

### Name Validation
- 2-50 characters
- Only letters, spaces, hyphens, apostrophes, and dots
- No consecutive special characters
- No numbers

### Email Validation
- Standard email format: `user@domain.com`
- Cannot start or end with a dot
- Domain must have at least one dot

### Indian Mobile Number Validation
Accepts the following formats:
- `9876543210` (10 digits)
- `+919876543210`
- `09876543210`
- `+91 9876543210`
- `+91-9876543210`
- `91 9876543210`

**Requirements:**
- Must be exactly 10 digits (after removing country code)
- Must start with 6, 7, 8, or 9
- Country code must be +91 or 91 (if provided)

### Date of Birth Validation
- Candidate must be between 16 and 100 years old

## Design Features

### Visual Elements
- **Gradient Background**: Purple gradient (#667eea to #764ba2)
- **Floating Icons**: Animated decorative icons in the background
- **Info Cards**: Three cards showing "Quick Process", "Secure & Private", and "Instant Submit"
- **Glassmorphism**: Semi-transparent form card with backdrop blur
- **Smooth Animations**: Hover effects, floating animations, and transitions

### Interactive Elements
- **Clickable Checkboxes**: Entire checkbox area is clickable (not just the checkbox itself)
- **Visual Feedback**: Checkboxes highlight when checked
- **Real-time Validation**: Fields validate as you type/blur
- **Loading States**: Submit button shows spinner during submission

## Customization

### Changing Colors
Edit the CSS variables in `index.html` (lines 13-24):

```css
:root {
  --primary: #2c3e50;
  --secondary: #3498db;
  --accent: #e74c3c;
  /* ... etc */
}
```

### Changing Gradients
```css
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Modifying Info Cards
Edit the info cards section in `index.html` (around line 460):
- Change icons by replacing the Font Awesome class
- Update text in `<h4>` and `<p>` tags

## Troubleshooting

### Technology options not loading?
1. Check that your Google Apps Script is deployed as a Web App
2. Verify the `scriptUrl` in `script.js` is correct
3. Check browser console for errors
4. Ensure "TechnologyOptions" sheet exists with data in column A

### Form submissions not appearing in Google Sheets?
1. Verify the "Submissions" sheet exists with correct headers
2. Check that the Apps Script has permission to edit the sheet
3. Look at the Apps Script execution logs (View → Executions)

### CORS errors?
- The script uses `mode: 'no-cors'` which should prevent CORS issues
- If you still see errors, verify the Apps Script is set to "Anyone" access

## Browser Support

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

## Security Notes

- Form data is sent to your Google Sheet (not a third-party service)
- All validation happens client-side before submission
- Google Apps Script runs with your permissions
- Consider adding reCAPTCHA for production use to prevent spam

## License

Part of antonnie.dev website.
