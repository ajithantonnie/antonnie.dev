# Badminton Club Attendance System Setup Instructions

## Prerequisites
1. Google Account with access to Google Sheets and Google Apps Script
2. Create a new Google Sheet or use existing one (you'll need the Sheet ID)

## Setup Steps

### Step 1: Prepare Google Sheets
1. Create a new Google Sheet or open your existing sheet
2. Copy the Sheet ID from the URL (the part after `/d/` and before `/edit`)sendAttendanceReminder
   - Example: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`
3. The system will automatically create three required sheets:
   - **Attendance** (with columns: Date, Name, Email, Availability, Reason, Attended, Warning Count, Missed Days, AutoRemove)
   - **Players** (with columns: Name, Email, Password)
   - **Hosts** (with columns: Name, Password, Role, IsAdmin, Email)

### Step 2: Set Up Google Apps Script
1. In your Google Sheet, go to **Extensions** > **Apps Script**
2. Delete the default `Code.gs` content
3. Copy and paste the content from the `Code.gs` file provided
4. **IMPORTANT**: Update the `SHEET_ID` constant at the top of the script with your actual Google Sheet ID:
   ```javascript
   const SHEET_ID = 'YOUR_SHEET_ID_HERE';
   ```
5. Save the project with a meaningful name (e.g., "Badminton Attendance System")

### Step 3: Initialize the System
1. In Google Apps Script, run the `initializeSheets()` function once:
   - Click on the function dropdown and select `initializeSheets`
   - Click the "Run" button
   - Grant necessary permissions when prompted
   - This creates the three required sheets with proper headers
2. Run the `setupTriggers()` function once:
   - Select `setupTriggers` from the dropdown
   - Click "Run"
   - This sets up automatic daily tasks and scheduled triggers:
     - **dailySetup**: Creates daily attendance entries at 8:00 AM IST
     - **sendAttendanceReminder**: Reminds players who haven't updated at 8:00 PM IST
     - **markMissingPlayersAsNo**: Auto-marks missing players as "No" at 10:30 PM IST
     - **sendAvailabilitySummaryEmail**: Sends final player list at 10:30 PM IST
     - **autoSetAttendedToAvailability**: Sets attendance based on availability at 12:01 AM IST
     - **checkWarningsAndInactivity**: Checks warnings and inactivity at 11:00 PM IST
     - **sendCelebrationIfFourAvailable**: Checks for 4 available players every 10 minutes (all day)

### Step 4: Deploy as Web App
1. In Google Apps Script, click "Deploy" > "New deployment"
2. Choose "Web app" as the type
3. Set the following configurations:
   - Description: "Badminton Attendance System"
   - Execute as: "Me"
   - Who has access: "Anyone" (or "Anyone with Google account" for more security)
4. Click "Deploy"
5. Copy the Web App URL (it will look like: `https://script.google.com/macros/s/[SCRIPT_ID]/exec`)

### Step 5: Update HTML File
1. Open `index.html`
2. Find this line near the top of the JavaScript section (around line 1144):
   ```javascript
   const SCRIPT_URL = 'YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE';
   ```
3. Replace the URL with your actual Web App URL from Step 4
4. **IMPORTANT**: Also update the page link in `Code.gs` if you want email links to work:
   - Find the line: `var link = "page link";` (around line 9)
   - Replace with your hosted page URL

### Step 6: Host the HTML File
You can host the HTML file in several ways:
1. **GitHub Pages** (Free):
   - Create a GitHub repository
   - Upload `index.html`
   - Enable GitHub Pages in repository settings
   
2. **Google Sites** (Free):
   - Create a new Google Site
   - Embed the HTML using an HTML embed component
   
3. **Any web hosting service** (Netlify, Vercel, etc.)

### Step 7: Initial Setup
1. Open your hosted HTML page
2. The system will automatically detect that no players/hosts exist
3. You'll see an "Initial Setup" section
4. Enter:
   - Your name
   - Your email address
   - A secure password (will be hashed automatically)
5. Click "Setup as Main Host"
6. You are now set up as both a player and the main Host (admin)!
7. You can now:
   - Add other players
   - Promote players to Co-Hosts or Hosts
   - Start using the attendance system

## System Features

### Password Security
- All passwords are hashed using SHA-256 with salt before storage
- Passwords are hashed client-side in the browser
- Host and admin authentication required for sensitive operations
- Session management with 30-minute timeout
- Session tokens stored in sessionStorage (cleared on browser close)

### Automatic Daily Tasks & Triggers
The system automatically (all times in IST - Asia/Kolkata):
- **8:00 AM**: Creates daily attendance entries for all players (default: Available "Yes")
- **9:00 PM**: Sends email reminder ONLY to players who haven't updated their availability for tomorrow
- **10:30 PM**: Marks missing players as "No" and sends final availability summary email to all players
- **12:01 AM**: Automatically sets "Attended" field to match "Availability" from previous day
- **11:00 PM**: Checks for warnings and inactivity, updates warning counts and missed days
- **Every 10 minutes (all day)**: Checks if 4 players are available and sends celebration email

### Email Notifications
The system sends emails for:
1. **Celebration Email**: When exactly 4 players mark "Yes" for tomorrow (sent to those 4 players)
2. **Opt-out Alert**: When count drops from 4 to 3 (someone backed out)
3. **Attendance Reminder**: At 9 PM to players who haven't updated for tomorrow
4. **Availability Summary**: At 10:30 PM with final list of confirmed players for tomorrow

### Player Workflow
1. Players must submit availability by 10:30 PM IST the day before (cutoff strictly enforced)
2. They select "Yes" or "No" for tomorrow's session
3. If selecting "No", they **must** provide a reason (required field)
4. If selecting "Yes", reason field is automatically cleared
5. Must enter their exact name and email (case-insensitive, must match Players sheet)
6. Must enter their password (set during initial player creation)
7. Can update their availability multiple times before the 10:30 PM cutoff
8. Players who don't update by 10:30 PM are automatically marked as "No"

### Host Workflow
1. Hosts can update actual attendance for TODAY only (before 10:00 AM IST - restriction removed in current code)
2. Must authenticate with:
   - Host name (dropdown selection)
   - Host email
   - Host password (hashed)
3. Select player to update from dropdown
4. Mark player as "Yes" (attended) or "No" (did not attend)
5. System automatically applies warning logic:
   - If player marked available but didn't attend: warning added
   - Warnings tracked in "Warning Count" column
   - "Missed Days" tracked separately
6. Host can update attendance multiple times for the same player on the same day

### Admin Management
As a Host (admin), you can:
1. **Add Players**: 
   - Enter player name, email, and password
   - Password is hashed before storage
   - Email validation is performed
   - Player is added to Players sheet
2. **Remove Players**: 
   - Select player from dropdown (shows name and email)
   - Cannot remove yourself (admin)
   - If player is also a host/co-host, they're removed from both sheets
3. **Add Hosts/Co-Hosts**: 
   - Can only promote existing players to Host or Co-Host role
   - Player must exist in Players sheet first
   - Uses player's existing password
   - Two roles available:
     - **Host**: Full admin access (can add/remove anyone)
     - **Co-Host**: Limited access (cannot remove hosts)
4. **Remove Hosts/Co-Hosts**: 
   - Cannot remove yourself
   - Co-Hosts cannot remove any hosts
   - Removes from Hosts sheet but keeps as player
5. **View Attendance**: See all attendance records with dates, availability, and attendance status
6. **Monitor Player Status**: View warnings, missed days, and auto-remove flags

### Roles and Permissions
- **Host (Admin)**: 
  - Full system access
  - Can add/remove players
  - Can add/remove hosts and co-hosts
  - Can update attendance
  - `IsAdmin` flag set to `true`
- **Co-Host**: 
  - Can add/remove players
  - Can add other co-hosts
  - **Cannot** remove hosts
  - Can update attendance
  - `IsAdmin` flag set to `false`
- **Player**: 
  - Can only update their own availability
  - No management access

### Warning System
The system automatically tracks and applies warnings:

**Warning Triggers:**
- Player marks "Yes" for availability but does NOT attend: **+1 warning**

**Automatic Removal Triggers:**
- **5 warnings accumulated**: Player marked for auto-removal
- **More than 15 missed days in current month**: Player marked for auto-removal
- **10 or more "No" responses without valid reasons in current month**: Player marked for auto-removal

**Warning Logic Details:**
- Warnings only apply when: `Availability = "Yes"` AND `Attended = "No"`
- If availability is "No", no warning is given (regardless of attendance)
- Warning count is cumulative across all time
- Missed days counter resets monthly
- "AutoRemove" flag is set when any threshold is reached
- System checks warnings and inactivity at 11:00 PM IST daily

**Tracking Properties:**
- Uses Google Apps Script Properties Service to track daily status
- Tracks celebration emails sent (prevents duplicates)
- Tracks player count changes (for opt-out detection)
- Automatically cleans up old tracking properties

## Security Features
- **Client-side password hashing**: SHA-256 with salt ("badminton_salt_2025") + base64 encoding
- **Host authentication required**: Name, email, and password verification for attendance updates
- **Admin authentication required**: Password verification for system management
- **Time-based restrictions**: 
  - Player cutoff: 10:30 PM IST (cannot submit after this time)
  - Host update: Anytime (no time restriction in current code)
- **Role-based access control**: Host vs Co-Host permissions
- **Session management**: 
  - 30-minute timeout with automatic logout
  - Session token stored in sessionStorage (cleared on browser close)
  - Auto-extends session on user activity (click, keypress, mousemove, scroll)
  - Session monitoring every 30 seconds
- **Secure token generation**: Cryptographically secure random tokens (32 bytes)
- **Email validation**: Regex pattern validation for all email inputs
- **Password matching**: Case-insensitive name/email matching with exact password hash comparison
- **Self-removal prevention**: Admins cannot remove themselves
- **Co-Host restrictions**: Co-Hosts cannot remove Hosts

## Troubleshooting

### Common Issues

1. **"Error loading data from Google Sheets"**
   - Check if the Web App URL is correct in `index.html` (line ~1144)
   - Ensure the Google Apps Script is deployed as Web App
   - Verify the `SHEET_ID` in `Code.gs` matches your actual Google Sheet ID
   - Check if the deployment is set to "Anyone" access
   - Try redeploying the Web App (Deploy > New deployment)

2. **"Network error. Please try again."**
   - Check internet connection
   - Verify the Google Apps Script deployment is active
   - Check browser console for CORS errors
   - Try clearing browser cache and cookies

3. **"Invalid admin credentials" or "Invalid host credentials"**
   - Ensure you've completed the initial setup (Step 7)
   - Verify password is correct (case-sensitive)
   - Check that email matches exactly (case-insensitive)
   - Password mismatch debug info is logged in Apps Script logs
   - Ensure player exists in both Players and Hosts sheets

4. **"Player not found" errors**
   - Verify player name and email match exactly (case-insensitive, whitespace trimmed)
   - Check Players sheet to confirm player exists
   - Ensure player has a password set

5. **"Cutoff time passed" messages**
   - Player submissions locked after 10:30 PM IST
   - Must wait until next day (after 8 AM when new entries are created)
   - Check system time is correct

6. **Triggers not firing**
   - Go to Apps Script > Triggers tab
   - Check if triggers are listed and active
   - Re-run `setupTriggers()` function if needed
   - Ensure project timezone is set to "Asia/Kolkata" (IST)
   - Check trigger execution logs for errors

7. **"Cannot remove yourself" error**
   - System prevents admins from removing their own account
   - Another admin must remove you if needed

8. **Password not working after initial setup**
   - Clear browser cache/cookies
   - Check if password hash matches in Players sheet
   - Password is hashed with SHA-256 + salt + base64
   - Try resetting password by editing Players sheet directly (use same hashing method)

### Testing the Setup
1. **Test Initial Setup**:
   - Open hosted page, should show "Initial Setup" section
   - Create first host with name, email, password
   - Should redirect to management panel after success

2. **Test Player Availability Submission**:
   - Enter player name and email (must match Players sheet)
   - Enter password
   - Select "Yes" or "No" for tomorrow
   - If "No", must provide reason
   - Submit before 10:30 PM IST cutoff
   - Check Attendance sheet for new entry

3. **Test Host Attendance Update**:
   - Select host name from dropdown
   - Enter host email and password
   - Select player from dropdown
   - Mark as "Yes" or "No" for attendance
   - Check Attendance sheet for updated "Attended" field

4. **Test Admin Functions**:
   - Login as admin (host with IsAdmin=true)
   - Try adding a new player (name, email, password)
   - Try promoting a player to Co-Host or Host
   - Try removing a player
   - View attendance data
   - Check player status

5. **Test Automated Features**:
   - Wait for 8:00 AM IST - check if daily entries are created
   - Wait for 9:00 PM IST - check if reminder emails are sent
   - Submit 4 "Yes" responses - check if celebration email is sent
   - Wait for 10:30 PM IST - check if missing players marked as "No"
   - Wait for 11:00 PM IST - check if warnings are applied
   - Wait for 12:01 AM IST - check if "Attended" is set

6. **Test Warning System**:
   - Mark player available ("Yes") but don't attend ("No")
   - Check if warning count increases
   - Accumulate 5 warnings - check if AutoRemove flag is set

7. **Verify Data in Google Sheets**:
   - Open your Google Sheet
   - Check Attendance sheet for entries
   - Check Players sheet for player list with passwords (hashed)
   - Check Hosts sheet for host list with roles and emails

## Maintenance

### Regular Tasks
- **Daily**: Monitor attendance entries and player participation
- **Weekly**: Review warning counts and missed days
- **Monthly**: Check for auto-removed players and clean up if needed
- **As needed**: Add/remove players and hosts

### Important Notes
- Regularly check Google Sheets for data integrity
- Monitor the Google Apps Script execution logs (Apps Script > Executions)
- Check trigger status in Apps Script > Triggers tab
- If triggers stop working, re-run `setupTriggers()` function
- Keep Sheet ID and Web App URL updated in both `Code.gs` and `index.html`
- **Project Timezone**: Must be set to "Asia/Kolkata" (IST) in Apps Script project settings
- **Script Timezone**: Set via `TIMEZONE = 'Asia/Kolkata'` constant in `Code.gs`

### Sheet Structure
**Attendance Sheet Columns** (9 columns):
1. Date (YYYY-MM-DD format)
2. Name
3. Email
4. Availability (Yes/No)
5. Reason (text, required if No)
6. Attended (Yes/No)
7. Warning Count (number)
8. Missed Days (number)
9. AutoRemove (text flag)

**Players Sheet Columns** (3 columns):
1. Name
2. Email
3. Password (SHA-256 hash + base64)

**Hosts Sheet Columns** (5 columns):
1. Name
2. Password (SHA-256 hash + base64, same as Players)
3. Role (Host/Co-Host)
4. IsAdmin (boolean: true for Host, false for Co-Host)
5. Email

### Backup Recommendations
- Regularly export Google Sheet data to CSV
- Keep a backup of `Code.gs` and `index.html`
- Document any customizations made to the system
- Save Web App URL and Sheet ID in a secure location

## Support
If you encounter issues:
1. Check the Google Apps Script execution transcript for detailed error logs
2. Verify all permissions are granted to the script
3. Ensure the Google Sheet is accessible and has the correct structure
4. Check browser console (F12) for JavaScript errors
5. Review trigger execution history in Apps Script
6. Verify timezone settings match (Asia/Kolkata)
7. Test with simple operations first (view data) before complex ones (admin functions)

## Advanced Customization

### Changing Time Restrictions
Edit these sections in `Code.gs`:
- **Player cutoff**: `submitPlayerAttendance()` function (line ~506-509)
- **Host update time**: Currently no restriction, add check in `submitHostAttendance()` if needed

### Changing Email Content
Edit these functions in `Code.gs`:
- `sendAttendanceReminder()` - 8 PM reminder email
- `sendAvailabilitySummaryEmail()` - 10:30 PM summary email
- `sendCelebrationIfFourAvailable()` - 4-player celebration email

### Changing Warning Thresholds
Edit in `checkWarningsAndInactivity()` function (line ~119-176):
- Warning threshold: Currently 5 warnings
- Missed days threshold: Currently 15 days per month
- Invalid "No" threshold: Currently 10 per month

### Changing Trigger Times
Re-run `setupTriggers()` after modifying trigger times in the function (line ~1125-1195).

### Customizing UI
Edit `index.html` styles and layout:
- CSS variables: lines 8-14 (colors)
- Card layouts: lines 50-60
- Form styles: lines 74-89
- Responsive breakpoints: line 530+