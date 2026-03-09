# Quick Setup Guide - Google Sheets Integration

## 🚀 5-Minute Setup

### Step 1: Create Google Sheet (1 minute)
1. Go to https://sheets.google.com
2. Click "+ Blank" to create new sheet
3. Rename it to "Recruitment Referrals"

### Step 2: Create Two Sheets (1 minute)

**Sheet 1: Rename "Sheet1" to "Submissions"**
Add these headers in Row 1:
```
A1: Timestamp
B1: First Name
C1: Last Name
D1: Email
E1: Date of Birth
F1: Mobile Number
G1: Technology/Role
H1: LinkedIn Company
I1: LinkedIn Profile
```

**Sheet 2: Create new sheet named "TechnologyOptions"**
Add header and options:
```
A1: Technology Options
A2: Java Backend
A3: Java Fullstack
A4: UI/UX Designer
A5: Frontend Developer
A6: Python Developer
A7: DevOps Engineer
A8: Data Scientist
A9: Mobile App Developer
A10: QA Engineer
A11: Cloud Architect
```

### Step 3: Add Apps Script (2 minutes)
1. Click **Extensions** → **Apps Script**
2. Delete existing code
3. Copy the entire script from README.md (the big code block)
4. Paste it
5. Click Save icon (💾)
6. Name it "Recruitment Form Handler"

### Step 4: Deploy (1 minute)
1. Click **Deploy** → **New deployment**
2. Click gear icon ⚙️ → Select **Web app**
3. Set:
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Click **Deploy**
5. Click **Authorize access**
6. Choose your Google account
7. Click **Advanced** → **Go to Recruitment Form Handler**
8. Click **Allow**
9. **COPY THE WEB APP URL** (looks like: `https://script.google.com/macros/s/AKfycby.../exec`)

### Step 5: Update Website Code (30 seconds)
1. Open `recruitment/script.js`
2. Find line 3
3. Replace:
   ```javascript
   scriptUrl: 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec',
   ```
   With:
   ```javascript
   scriptUrl: 'YOUR_ACTUAL_URL_FROM_STEP_4',
   ```
4. Save the file

### ✅ Done! Test it:
1. Open your recruitment page
2. The dropdown should show your technology options
3. Submit a test form
4. Check your Google Sheet - the data should appear!

---

## 📝 How to Update Technology Options

**Super Easy - No Code Required!**

1. Open your Google Sheet
2. Go to "TechnologyOptions" tab
3. Add/Edit/Delete rows in column A
4. Changes appear on website immediately!

Example:
```
A2: Java Backend          ← Keep
A3: Java Fullstack        ← Keep
A4: UI/UX Designer        ← Edit to "Senior UI/UX Designer"
A5: Frontend Developer    ← Delete this row
A6: React Developer       ← Add new option
```

---

## 🔍 Troubleshooting

### Problem: Dropdown shows fallback options only
**Solution:** 
- Check that Apps Script is deployed
- Verify the URL in script.js is correct
- Check browser console (F12) for errors

### Problem: Form submits but data doesn't appear in sheet
**Solution:**
- Verify "Submissions" sheet name is exact
- Check column headers match exactly
- View Apps Script logs: Apps Script → View → Executions

### Problem: "Authorization required" error
**Solution:**
- Redeploy the Apps Script
- Make sure "Who has access" is set to "Anyone"

---

## 📊 Viewing Submissions

All form submissions appear in the "Submissions" sheet with:
- Timestamp (when submitted)
- All form fields
- LinkedIn checkbox responses (Yes/No)

You can:
- ✅ Sort and filter data
- ✅ Export to Excel/CSV
- ✅ Create charts and reports
- ✅ Share with team members
- ✅ Set up email notifications (using Apps Script triggers)

---

## 🎨 Customization Tips

### Change Form Colors
Edit `index.html`, find the `:root` section (around line 13):
```css
--primary: #2c3e50;      /* Dark blue */
--secondary: #3498db;    /* Light blue */
--accent: #e74c3c;       /* Red for errors */
```

### Change Background Gradient
Find `body` style (around line 50):
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Try these beautiful gradients:
- Ocean: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Sunset: `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)`
- Forest: `linear-gradient(135deg, #0ba360 0%, #3cba92 100%)`
- Night: `linear-gradient(135deg, #2c3e50 0%, #34495e 100%)`

### Add More Info Cards
Find the info-cards section (around line 460) and duplicate:
```html
<div class="info-card">
  <i class="fas fa-your-icon"></i>
  <h4>Your Title</h4>
  <p>Your description</p>
</div>
```

Find icons at: https://fontawesome.com/icons

---

## 🔐 Security Best Practices

1. **Never share your Apps Script URL publicly** (it's in your code, that's fine)
2. **Review submissions regularly** for spam
3. **Consider adding reCAPTCHA** for production
4. **Limit Google Sheet access** to only those who need it
5. **Set up data retention policies** (delete old submissions)

---

## 📱 Mobile Validation Examples

Valid Indian mobile numbers:
- ✅ `9876543210`
- ✅ `+919876543210`
- ✅ `+91 9876543210`
- ✅ `+91-9876-543-210`
- ✅ `09876543210`

Invalid:
- ❌ `1234567890` (doesn't start with 6-9)
- ❌ `98765` (too short)
- ❌ `+1 234 567 8900` (not Indian country code)

---

## 🎯 Next Steps

1. **Test thoroughly** with various inputs
2. **Share the link** with your team
3. **Monitor submissions** in Google Sheets
4. **Update technology options** as needed
5. **Customize the design** to match your brand

Need help? Check the full README.md for detailed documentation!
