# Subscription Manager
A simple PyQT5 interface with Sqlite3 database to tack one's Clients and monitor their Subscriptions over time.

# 🛠 Functionality
The database stores Clients (ID, Name, Tel, Email, Level, Last Activity) and their Subscriptions (ID, Holder, Issue Date, End Date, Type(1/3/6/12), Status(ACTIVE/ENDED), Days Frozen)
One may enter, edit, and remove the entires. The Subscriptions can be Frozen for a certain amount of days.
The main window features a quick search using the Client's Name or Tel and two tables showing the Subscriptions that are ending or have ended within a week. 
Two menues: Menu and DB. The former comprises "All Clients", "All Subscriptions" and "Statistics" (for 1 week/2 weeks/month). A backup copy of the DB can be made.
The option to Freeze All Active Subscriptions is available in Menu -> "All Subscriptions".

# ⌨️ Characteristics
- The default date format is dd/MM/yyyy.
- The default DB directory is "DB\\Main.db". Can be set using the DB_PATH const in db.py. 
- The DB can be temporarily changed using Menu -> "Load DB". The default password to do so is "admin".
- Freezing all active subs will extend the respective End Dates for an amount of days up to 60, which will be added to their Days Frozen.
- Double clicking the Subscription or Client entries will pop up the respective editing windows.
- Logging is done into \History.log. It stores info on all Subscriptions EDITS and FREEZEs.

# 🖥 Interface
<a href="https://i.ibb.co/tJ4Rbjp/Subscription-Manager-Interface.png">
  <img src="https://i.ibb.co/tJ4Rbjp/Subscription-Manager-Interface.png" width="256" alt="Screen" />
</a>
