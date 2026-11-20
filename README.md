# The Premium Studio Unisex Salon

A starter Flask website with guest appointment requests and a private admin dashboard.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run:

   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000`.

## Initial admin login

- Username: `admin`
- Password: `ChangeMe123!`

Change these before using the site with real customers. Set environment variables `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a long random `SECRET_KEY` before the first run/deployment. The initial admin account is created only when the database has no admin account.

## Booking behaviour and important limitations

- Customers do not need an account, email address, or password.
- The form asks for name, phone, service, date and time.
- Only one booking can be saved for the exact same date and time.
- Opening hours are validated: Monday-Friday 09:00-22:00; Saturday-Sunday 08:00-22:30.
- Appointment duration and fixed slot intervals have not been supplied. This first version therefore accepts a selected time and prevents duplicate exact times; it does not yet prevent overlapping appointments of different start times. Confirm service durations and the salon's desired interval before using this as a live scheduling system.
- The admin can view bookings and update their status.
- WhatsApp link and salon phone are set to the supplied number.

## Before public launch

- Set a strong `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
- Turn off Flask debug mode (change `app.run(debug=True)` to `app.run()` or use a production WSGI server).
- Use HTTPS and a production database with persistent storage/backups. Local SQLite may not persist on some hosting configurations.
- Add CSRF protection, rate limiting, stronger phone validation, privacy notice and a secure password-change process.
- Add real salon photos and verify the map link.
- Google reviews are not automatically imported in this starter version. A Google-approved API or review provider/widget would need to be configured.
- Test bookings, admin access and time-zone/date handling before accepting real customers.
