# Google Drive Integration Setup

This document explains how to set up the Precision Rifle Load Development application to use Google Drive for storing test data. This allows you to access your test data from multiple computers.

## Overview

The application stores test data in directories that you configure. By default, the application uses a directory called `tests` in the application's root directory. However, you can configure the application to use directories in your Google Drive folder instead.

The application now supports multiple database pointers, allowing you to switch between different test databases easily. Each database pointer has a label and a path to a directory containing test data.

## Setup Instructions

### Step 1: Install Google Drive Desktop Client

First, you need to install the Google Drive desktop client on your computer:

1. Download the Google Drive desktop client:
   - Windows/macOS: [Google Drive for Desktop](https://www.google.com/drive/download/)
   - Linux: Use [Insync](https://www.insynchq.com/) or another Google Drive client

2. Install and set up the client according to the instructions.

3. Make sure Google Drive is syncing to your computer.

### Step 2: Create Test Directories in Google Drive

1. Open your Google Drive folder on your computer.

2. Create folders for your test databases. For example:
   - `competition_tests` - For competition load data
   - `development_tests` - For load development data
   - `factory_ammo_tests` - For factory ammunition test data

### Step 3: Configure the Application

1. Open the Precision Rifle Load Development application.

2. Click on **File > Settings** in the menu bar.

3. In the Settings dialog, you'll see a list of database pointers on the left and database details on the right.

4. To add a new database pointer:
   - Click the **Add** button
   - Enter a label for the database (e.g., "Competition Loads")
   - Enter the path to the directory in your Google Drive or click **Browse** to select it:
     - **Windows**: Typically `C:\Users\YourUsername\Google Drive\competition_tests` or `C:\Users\YourUsername\My Drive\competition_tests`
     - **macOS**: Typically `/Users/YourUsername/Google Drive/competition_tests` or `/Users/YourUsername/My Drive/competition_tests`
     - **Linux**: Depends on your Google Drive client, but typically `~/Google Drive/competition_tests` or `~/google-drive/competition_tests`
   - Click **Update** to add the database

5. To set a database as active:
   - Select the database in the list
   - Click **Set as Active**

6. Click **Close** to close the Settings dialog.

## Using Multiple Databases

The application now supports multiple database pointers, allowing you to switch between different test databases easily:

1. **Database Indicator**: The active database is shown in the window title and status bar.

2. **Switching Databases**: To switch to a different database:
   - Open the Settings dialog
   - Select the database you want to use
   - Click **Set as Active**
   - The application will automatically refresh to show the tests from the new database

3. **Managing Databases**: You can:
   - **Add** new database pointers
   - **Update** existing database pointers (change the label or path)
   - **Delete** database pointers you no longer need
   - **Set** a database as the active database

## Using the Application with Google Drive

Once you've set up the Google Drive integration, the application will store test data in your Google Drive folders. This means:

1. All new tests you create will be saved to the active database in Google Drive.
2. All existing tests will be loaded from the active database in Google Drive.
3. Any changes you make to tests will be saved to Google Drive.

Google Drive will automatically sync your test data to the cloud and to any other computers where you've set up the Google Drive client.

## Troubleshooting

### Tests Not Showing Up

If your tests are not showing up in the application:

1. Make sure Google Drive is syncing properly.
2. Check that the path to the tests directory is correct in the database settings.
3. Make sure you're using the correct database (check the active database indicator).
4. Restart the application.

### Changes Not Syncing

If changes to your tests are not syncing to other computers:

1. Make sure Google Drive has finished syncing on both computers.
2. Check your internet connection.
3. Try closing and reopening the application.

### Permission Issues

If you encounter permission issues:

1. Make sure you have read and write permissions for the tests directory.
2. Try running the application as an administrator (Windows) or with sudo (Linux).

## Using Multiple Computers

To use the application with the same test data on multiple computers:

1. Install the Google Drive desktop client on each computer.
2. Configure the application on each computer with the same database pointers.
3. Make sure Google Drive is syncing on each computer before using the application.

## Backup Recommendations

Even though Google Drive provides some backup functionality, it's still recommended to:

1. Regularly back up your test data to another location.
2. Consider enabling Google Drive's version history feature to recover from accidental changes.
3. Use multiple databases to organize your data and reduce the risk of data loss.
