import subprocess

# List of packages for which we want to find the version
packages = [
    "fastapi",
    "uvicorn",
    "openai",
    "python-dotenv",
    "requests",
    "llama-index",
    "sqlalchemy",
    "pydantic",
    "streamlit",
    "streamlit-authenticator",
    "google-cloud-firestore",
    "google-generativeai",
]

def get_package_version(package_name):
    try:
        # Use pip show to get the package version
        result = subprocess.run(["pip", "show", package_name], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to find the version line
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    return line.split(" ")[1]
    except Exception as e:
        print(f"Error getting version for package {package_name}: {e}")
    return "Not found"

def main():
    with open("requirements.txt", "w") as req_file:
        for package in packages:
            version = get_package_version(package)
            if version != "Not found":
                req_file.write(f"{package}=={version}\n")
            else:
                print(f"Version not found for {package}, you might want to check this package manually.")

if __name__ == "__main__":
    main()
