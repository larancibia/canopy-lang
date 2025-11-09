#!/bin/bash
# Desencriptar archivos con "Tengo 1 hermana!"

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

echo -e "${YELLOW}🔓 Desencriptando archivos...${NC}"

# Buscar y desencriptar TODOS los archivos .enc
find . -name "*.enc" -type f | while read -r enc_file; do
    output="${enc_file%.enc}"
    if sops decrypt "$enc_file" > "$output" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $output"
    fi
done

echo -e "${GREEN}✅ Listo! Los archivos .env están disponibles${NC}"
