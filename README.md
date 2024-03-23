# CSV Type-Infer Project

Welcome to the CSV Cleaner project! This document provides instructions on setting up the project environment, running the server, and executing backend tests.
[Click here to watch the video](screen_recording.mp4)

## Prerequisites

- Python 3.10
- Poetry (Python package and dependency manager)

## Installation Guide

### Install Python 3.10

Ensure that Python 3.10 is installed on your system. You can download it from the official Python website: [Python Downloads](https://www.python.org/downloads/).

### Install Poetry

Install Poetry for handling project dependencies. You can install Poetry by following the instructions on the official website: [Poetry Installation](https://python-poetry.org/docs/#installation).

### Clone the Project

Clone the project repository to your local machine:

    git clone <repository-url>


Replace `<repository-url>` with the actual URL of the project repository.

### Install Project Dependencies

Navigate to the project directory and install the required libraries using Poetry:

    poetry install

This command reads the `pyproject.toml` file and installs the dependencies specified.

## Running the Server

To start the project server, first navigate to the `src` directory:

    cd src


Then, start the Django development server with the following command:

    poetry run python manage.py runserver

The server will start, and you can access the application by navigating to `http://127.0.0.1:8000/` in your web browser.

## Running Backend Tests

If you wish to run backend tests for the project, use the following command:

    poetry run pytest --ds=config.settings

This command executes all the test cases using `pytest`, with Django settings specified by `_config.settings`. Ensure you adjust `_config.settings` if your settings path differs.

## Front-end Setup

### Prerequisites

- Node.js
- npm (Node Package Manager)
- React 18

### Installing Node.js and npm

Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine, and npm is its package manager. You can download and install them from the [official Node.js website](https://nodejs.org/).

### Installing React 18

React is a JavaScript library for building user interfaces. It is maintained by Facebook and a community of individual developers and companies. React 18 can be added to a project via npm.

Since you will be using `npm` to manage your front-end packages, you do not need to install React globally on your system for this project. React and other necessary libraries will be listed as dependencies in your project's `package.json` file and installed into the project directory.

### Setting Up the Front-end Project

After installing Node.js and npm, navigate to the front-end project directory:

    cd frontend/csv-viewer

Then, install the project dependencies including React 18 by running:

    npm install

This command reads the `package.json` file in your project directory and installs all the listed dependencies into the `node_modules` folder.

### Running the Front-end Development Server

Start the development server with:

    npm start

This command starts a development server and opens a browser window pointing to `http://localhost:3000/`, where you can interact with the front-end application.

---

Thank you for setting up the project. Follow the steps above to get started with development.