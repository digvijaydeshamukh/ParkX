# 🚗 ParkX - Smart Parking Management System

## 📌 Project Overview

**ParkX** is a smart parking management system designed to automate vehicle parking without requiring human interaction. The system enables vehicle owners to search for parking spaces, reserve slots, make online payments, and use QR codes for seamless entry and exit.

The primary objective of ParkX is to reduce manual parking management, optimize parking space utilization, and provide a smooth user experience for both vehicle owners and parking owners.

---

# ✨ Features

## Vehicle Owner

* User Registration & Login
* Manage Profile
* Register Multiple Vehicles
* Search Nearby Parking Areas
* View Available & Reserved Parking Slots
* Reserve Parking Slot
* Online Payment
* QR Code Generation
* QR Based Entry & Exit
* Parking Timer & Countdown
* Automatic Extra Charge Calculation
* Booking History
* Payment History
* Email Receipt & Notifications

---

## Parking Owner

* Register Parking Area
* Manage Parking Details
* Create Parking Slots
* Set Hourly / Daily Pricing
* View Live Parking Occupancy
* View Revenue Reports
* Manage Bookings

---

## Admin

* Manage Users
* Manage Parking Owners
* Manage Parking Areas
* Manage Bookings
* Manage Payments
* Dashboard & Reports

---

# 🛠️ Tech Stack

### Backend

* Python
* Django
* Django REST Framework

### Database

* MySQL 8

### Containerization

* Docker
* Docker Compose

### Authentication

* Django Authentication
* JWT Authentication (Planned)

### Other Libraries

* mysqlclient
* python-dotenv
* Pillow
* qrcode

---

# 📁 Project Structure

```text
ParkX/
│
├── backend/
│   ├── accounts/
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
│
├── docker/
│   ├── django/
│   ├── mysql/
│   └── redis/
│
├── docs/
├── frontend/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Install the following software:

* Git
* Docker Desktop
* Python (Optional for local development)

---

## Clone Repository

```bash
git clone https://github.com/digvijaydeshamukh/ParkX.git

cd ParkX
```

---

## Create Environment File

Create a `.env` file in the project root.

Example:

```env
MYSQL_DATABASE=parkx

MYSQL_USER=parkx_app

MYSQL_PASSWORD=your_password

MYSQL_ROOT_PASSWORD=your_root_password

DB_HOST=db

DB_PORT=3306
```

---

## Build Docker Containers

```bash
docker compose build
```

---

## Start Containers

```bash
docker compose up
```

or

```bash
docker compose up -d
```

---

## Run Database Migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Start Development Server

The server automatically starts when Docker Compose is running.

Open:

```
http://localhost:8000
```

Admin Panel:

```
http://localhost:8000/admin
```

---

# 🐳 Useful Docker Commands

## Stop Containers

```bash
docker compose down
```

## Restart Containers

```bash
docker compose restart
```

## Rebuild Images

```bash
docker compose up --build
```

## View Running Containers

```bash
docker compose ps
```

## View Logs

```bash
docker compose logs
```

---

# 🗄️ Database

Database: **MySQL 8**

The database runs inside a Docker container.

Host (inside Docker):

```
db
```

Host (Local Machine):

```
localhost
```

Port:

```
3307
```

---

# 📌 Development Workflow

```text
main
   │
develop
   │
feature/accounts
feature/parking
feature/booking
feature/payment
feature/dashboard
```

Every new feature should be developed in a separate feature branch and merged into `develop` before being merged into `main`.

---

# 📅 Development Roadmap

* Project Setup
* Docker Configuration
* Authentication Module
* Parking Management
* Slot Management
* Booking System
* QR Code Integration
* Payment Gateway
* Dashboard
* Email Notifications
* Reports
* REST APIs
* Testing
* Deployment

---

# 👥 Team

### Developer 1


### Developer 2



---

# 📄 License

This project is developed for learning, academic purposes, and portfolio demonstration.

---

**Project Name:** ParkX

**Status:** 🚧 Under Development
