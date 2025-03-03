# Making the HALO Portfolio Simulator Portable

This guide explains how to make the HALO Portfolio Simulator portable so you can share it with colleagues or move it to another computer.

## Option 1: Standalone Executable (Easiest for Non-Technical Users)

This creates a single executable file that can be run on any compatible computer without installing Python.

### Building the Executable

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```
   python build_app.py
   ```

3. The executable will be created in the `dist` directory along with a data package.

### Sharing the Executable

1. Share the executable file (`dist/HALO_Portfolio_Simulator_*.exe` or `dist/HALO_Portfolio_Simulator_*`)
2. Share the data package (`dist/portfolio_data_*.zip`)
3. Instruct users to:
   - Extract the data package to a folder named `data` in the same directory as the executable
   - Run the executable by double-clicking it

## Option 2: GitHub Repository (Best for Version Control)

This option uses Git to track changes and allows easy sharing via GitHub.

### Creating a Repository

1. Use the save_breakpoint.py script to initialize a Git repository:
   ```
   python save_breakpoint.py "Initial commit with working portfolio simulator"
   ```

2. Create a repository on GitHub (or similar service)

3. Link your local repository to GitHub:
   ```
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

### Sharing via GitHub

1. Share the GitHub repository URL with colleagues
2. They can clone the repository:
   ```
   git clone YOUR_GITHUB_REPO_URL
   cd portfolio_simulator
   pip install -r requirements.txt
   python run_gui.py
   ```

### Creating Breakpoints

To save your progress at any point:
```
python save_breakpoint.py "Description of your current progress"
```

To create a branch for a new feature:
```
python save_breakpoint.py "Starting work on new feature" --branch new-feature-name
```

## Option 3: Docker Container (Best for Consistency)

This option packages the application in a Docker container for consistent execution across platforms.

### Building the Docker Image

1. Install Docker on your system (from [docker.com](https://www.docker.com/))

2. Build the Docker image:
   ```
   docker build -t halo-portfolio-simulator .
   ```

### Running the Docker Container

For Linux:
```
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix halo-portfolio-simulator
```

For macOS (requires XQuartz):
```
xhost + 127.0.0.1
docker run -e DISPLAY=host.docker.internal:0 halo-portfolio-simulator
```

For Windows (requires X server like VcXsrv):
```
docker run -e DISPLAY=host.docker.internal:0 halo-portfolio-simulator
```

### Sharing the Docker Image

1. Push the image to Docker Hub:
   ```
   docker tag halo-portfolio-simulator yourusername/halo-portfolio-simulator
   docker push yourusername/halo-portfolio-simulator
   ```

2. Others can pull and run it:
   ```
   docker pull yourusername/halo-portfolio-simulator
   docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix yourusername/halo-portfolio-simulator
   ```

## Recommended Approach

For most users, the standalone executable (Option 1) is the easiest way to share the application. However, if you're actively developing the application, using Git (Option 2) provides better version control and collaboration features. 