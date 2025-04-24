# Precision Rifle Load Development Development Guidelines

This document provides guidelines for developers working on the Precision Rifle Load Development application. It covers development workflow, coding standards, and Git practices.

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A code editor (VS Code recommended)

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/lasit/precision-rifle-load-development-v3.git
   cd precision-rifle-load-development-v3
   ```

2. Set up a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   # Windows
   start_app.bat

   # macOS/Linux
   ./start_app.command
   ```

   Alternatively, you can run the Python script directly:
   ```bash
   python run.py
   ```

5. Terminating the application:
   ```bash
   # Windows
   kill_app.bat

   # macOS/Linux
   ./kill_app.sh
   ```

## Development Workflow

### Feature Development

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/feature-name
   ```

2. **Implement the Feature**:
   - Follow the coding standards
   - Write tests for the feature
   - Update documentation as needed

3. **Test the Feature**:
   - Run the application and test the feature manually
   - Run automated tests if available

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add feature: feature-name"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin feature/feature-name
   ```

6. **Create a Pull Request**:
   - Go to the GitHub repository
   - Create a pull request from your feature branch to the main branch
   - Provide a detailed description of the changes

### Bug Fixes

1. **Create a Bug Fix Branch**:
   ```bash
   git checkout -b fix/bug-name
   ```

2. **Fix the Bug**:
   - Identify the root cause
   - Make minimal changes to fix the issue
   - Add tests to prevent regression

3. **Test the Fix**:
   - Run the application and verify the bug is fixed
   - Run automated tests if available

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Fix bug: bug-name"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin fix/bug-name
   ```

6. **Create a Pull Request**:
   - Go to the GitHub repository
   - Create a pull request from your bug fix branch to the main branch
   - Provide a detailed description of the changes

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length of 100 characters
- Use docstrings for all classes and methods
- Use type hints where appropriate

### PyQt Code Style

- Use camelCase for method names (to match Qt conventions)
- Use descriptive names for widgets and variables
- Separate UI setup from business logic
- Use signals and slots for communication between components

### Documentation

- Update documentation when making changes
- Document all public methods and classes
- Include examples where appropriate
- Keep the README.md up to date

## Git Practices

### Branching Strategy

- `main`: The main branch containing stable code
- `feature/*`: Feature branches for new features
- `fix/*`: Bug fix branches for bug fixes
- `release/*`: Release branches for preparing releases

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update")
- Include the component or area affected
- Keep the first line under 50 characters
- Add more details in the commit body if needed

Examples:
- "Add settings dialog for database management"
- "Fix crash when loading invalid test data"
- "Update documentation for Google Drive integration"

### Pull Requests

- Create a pull request for each feature or bug fix
- Provide a detailed description of the changes
- Reference any related issues
- Request reviews from other developers
- Address review comments promptly

## Release Process

### Preparing a Release

1. Create a release branch:
   ```bash
   git checkout -b release/vX.Y.Z
   ```

2. Update version numbers:
   - Update version in the code
   - Update version in the documentation

3. Create a pull request to merge the release branch into main

4. After the pull request is approved and merged, create a tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. Create a release on GitHub with release notes

### Hotfixes

1. Create a hotfix branch from the tag:
   ```bash
   git checkout -b hotfix/vX.Y.Z.1 vX.Y.Z
   ```

2. Fix the issue

3. Update version numbers

4. Create a pull request to merge the hotfix branch into main

5. After the pull request is approved and merged, create a tag:
   ```bash
   git tag -a vX.Y.Z.1 -m "Hotfix vX.Y.Z.1"
   git push origin vX.Y.Z.1
   ```

6. Create a release on GitHub with release notes

## Application Startup and Shutdown

The application includes scripts for proper startup and shutdown on different platforms:

### Startup Scripts

- **start_app.command** (macOS/Linux): Checks for running instances, kills them, checks dependencies, and starts the application
- **start_app.bat** (Windows): Performs the same functions as the macOS/Linux script but with Windows-specific commands

These scripts ensure that:
- Only one instance of the application runs at a time
- All dependencies are installed
- The application starts with a clean environment

### Shutdown Scripts

- **kill_app.sh** (macOS/Linux): Kills any running instances of the application
- **kill_app.bat** (Windows): Kills any running instances of the application on Windows

These scripts ensure that:
- No orphaned processes are left running
- The application can be properly restarted without manual intervention

### Implementation Details

The startup scripts:
1. Check for running instances and kill them
2. Check if Python and pip are installed
3. Check if all dependencies are installed and install missing ones
4. Start the application

The shutdown scripts:
1. Find processes running the application
2. Terminate these processes
3. Provide feedback on the termination status

## Testing

### Manual Testing

- Test all features manually before submitting a pull request
- Test on different platforms if possible
- Test with different test data

### Automated Testing

- Write unit tests for critical functionality
- Run tests before committing changes
- Add tests for new features and bug fixes

## Conclusion

Following these development guidelines will help maintain a high-quality codebase and ensure a smooth development process. If you have any questions or suggestions for improving these guidelines, please create an issue on GitHub.
