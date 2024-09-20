# Stocks Transactions Handler

## Overview

The Stocks Transactions Handler is a django based basic web app,for implementing the basic and some advance concepts of django to practice and to get grip on django and DRF

## Features

- **User Registration and Authentication**: Users can register and authenticate using JWT tokens.
- **Stock Creation**: Admins can create and manage stock entries.
- **User Transactions**: Users can perform buy and sell transactions on specific stocks.
- **Token-Based Authentication**: Secure API access using JWT tokens.
- **API Endpoints**: Comprehensive API endpoints for managing users, stocks, and transactions.

## API Endpoints

### User Endpoints

- **`add_user`**: Creates a new user in the system.
- **`get_user_by_username`**: Retrieves user details by username.

### Stock Endpoints

- **`add_stock`**: Adds a new stock to the system.
- **`get_stock`**: Retrieves stock details by ticker symbol.
- **`get_all_stocks`**: Fetches a list of all stocks in the database.

### Transaction Endpoints

- **`add_transaction`**: Creates a new transaction for a user and a stock.
- **`get_transactions`**: Retrieves all transactions for a specific user.
- **`get_transactions_by_date`**: Fetches transactions for a user within a specified date range.

## Requirements

- **Python**: 3.10 or later
- **Django**: 5.1 or later
- **Django REST Framework**: 3.14 or later
- **PostgreSQL**: Database for storing user, stock, and transaction data
- **PyJWT**: For JWT token management

## Completed Features

- All functionalities related to user management, stock creation, and transaction handling are complete.

## In Progress

- JWT authentication and token generation are currently in progress.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd stocks_transactions_handler
