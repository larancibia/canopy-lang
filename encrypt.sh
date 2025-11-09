#!/bin/bash
# Encriptar archivos con "Tengo 1 hermana!"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Generar age key si no existe
if [ ! -f ~/.config/sops/age/keys.txt ]; then
    mkdir -p ~/.config/sops/age
    echo "Tengo 1 hermana!" | age-keygen > ~/.config/sops/age/keys.txt 2>/dev/null
    chmod 600 ~/.config/sops/age/keys.txt
fi

export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

echo -e "${YELLOW}🔐 Encriptando archivos...${NC}"

# Encriptar archivos .env (pero no los que ya son .enc)
find . -name ".env*" ! -name "*.enc" ! -name "*.example" -type f | while read -r env_file; do
    if sops encrypt "$env_file" > "${env_file}.enc.tmp" 2>/dev/null; then
        mv "${env_file}.enc.tmp" "${env_file}.enc"
        echo -e "${GREEN}✓${NC} ${env_file}.enc"
    fi
done

# También encriptar credentials.json si existe
if [ -f "credentials.json" ]; then
    sops encrypt credentials.json > credentials.json.enc 2>/dev/null && \
    echo -e "${GREEN}✓${NC} credentials.json.enc"
fi

echo -e "${GREEN}✅ Listo! Archivos encriptados${NC}"
