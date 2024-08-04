# ShluchimExplorer - Chabad Houses Management System

## Overview

The Chabad Houses Management System is a Python-based application designed to manage and interact with a database of Chabad houses. The system allows users to perform various operations including managing Chabad house information and activities. It integrates with a MySQL database to store and retrieve data.

## Features

- **User Authentication**: Secure login functionality for registered users.
- **Chabad House Management**: 
  - Add new Chabad houses.
  - Update existing Chabad house information.
  - Delete Chabad houses from the database.
- **Activity Management**:
  - Add activities to specific Chabad houses.
  - Remove activities from Chabad houses.
- **Search Functionality**:
  - Search for Chabad houses based on country and city.
  - View activities associated with Chabad houses.
  - Search for Chabad houses offering specific activities.
- **Guest Access**: Allows users to view general information about Chabad houses and their activities without needing to log in.

## Requirements

To run this project, you need the following Python package:

- `mysql-connector-python==8.0.33`

You can install the required package by running:

```bash
pip install -r requirements.txt
