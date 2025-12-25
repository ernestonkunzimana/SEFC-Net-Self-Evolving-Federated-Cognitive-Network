#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up SEFCNet development environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
pip install -r SEFCNet/requirements.txt

# Install development tools
echo -e "${YELLOW}Installing development tools...${NC}"
pip install black isort mypy pylint bandit pre-commit

# Initialize pre-commit hooks
echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
pre-commit install

echo -e "${GREEN}Setup complete!${NC}"
echo -e "\nTo activate the virtual environment:"
echo -e "    source venv/bin/activate"
echo -e "\nTo deactivate:"
echo -e "    deactivate"
echo -e "\nTo run the project:"
echo -e "    python SEFCNet/main.py"