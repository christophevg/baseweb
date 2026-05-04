#!/bin/bash
# download-vue3-vendor.sh
# Downloads Vue 3 + Vuetify 3 vendor files for baseweb migration
# Task: task-3.5

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base paths
VENDOR_JS="src/baseweb/static/vendor/js"
VENDOR_CSS="src/baseweb/static/vendor/css"
BACKUP_JS="src/baseweb/static/vendor/js.backup"
BACKUP_CSS="src/baseweb/static/vendor/css.backup"

# CDN base URLs
VUE_CDN="https://cdn.jsdelivr.net/npm"
UNPKG_CDN="https://unpkg.com"

echo -e "${BLUE}=== Vue 3 + Vuetify 3 Vendor File Download ===${NC}"
echo ""

# Step 1: Create backup directories
echo -e "${BLUE}Step 1: Creating backup directories...${NC}"
mkdir -p "$BACKUP_JS"
mkdir -p "$BACKUP_CSS"

# Step 2: Backup existing files
echo -e "${BLUE}Step 2: Backing up existing vendor files...${NC}"
if [ -d "$VENDOR_JS" ] && [ "$(ls -A $VENDOR_JS 2>/dev/null)" ]; then
    cp "$VENDOR_JS"/*.js "$BACKUP_JS/" 2>/dev/null || true
    echo -e "${GREEN}✓ JavaScript files backed up to $BACKUP_JS/${NC}"
else
    echo -e "${GREEN}✓ No existing JavaScript files to backup${NC}"
fi

if [ -d "$VENDOR_CSS" ] && [ "$(ls -A $VENDOR_CSS 2>/dev/null)" ]; then
    cp "$VENDOR_CSS"/*.css "$BACKUP_CSS/" 2>/dev/null || true
    echo -e "${GREEN}✓ CSS files backed up to $BACKUP_CSS/${NC}"
else
    echo -e "${GREEN}✓ No existing CSS files to backup${NC}"
fi

echo ""

# Step 3: Download Vue 3
echo -e "${BLUE}Step 3: Downloading Vue 3 global build...${NC}"
curl -fsSL -o "$VENDOR_JS/vue.js" "$VUE_CDN/vue@3/dist/vue.global.prod.js"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_JS/vue.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vue.js (Vue 3 global prod) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Vue 3${NC}"
    exit 1
fi

# Step 4: Download Vue Router 4
echo -e "${BLUE}Step 4: Downloading Vue Router 4 global build...${NC}"
curl -fsSL -o "$VENDOR_JS/vue-router.js" "$VUE_CDN/vue-router@4/dist/vue-router.global.prod.js"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_JS/vue-router.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vue-router.js (Vue Router 4 global prod) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Vue Router 4${NC}"
    exit 1
fi

# Step 5: Download Vuex 4
echo -e "${BLUE}Step 5: Downloading Vuex 4 global build...${NC}"
curl -fsSL -o "$VENDOR_JS/vuex.js" "$VUE_CDN/vuex@4/dist/vuex.global.prod.js"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_JS/vuex.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vuex.js (Vuex 4 global prod) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Vuex 4${NC}"
    exit 1
fi

# Step 6: Download Vuetify 3 JS
echo -e "${BLUE}Step 6: Downloading Vuetify 3 JavaScript...${NC}"
curl -fsSL -o "$VENDOR_JS/vuetify.js" "$VUE_CDN/vuetify@3/dist/vuetify.min.js"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_JS/vuetify.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vuetify.js (Vuetify 3 minified) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Vuetify 3 JS${NC}"
    exit 1
fi

# Step 7: Download Vuetify 3 CSS
echo -e "${BLUE}Step 7: Downloading Vuetify 3 CSS...${NC}"
curl -fsSL -o "$VENDOR_CSS/vuetify.min.css" "$VUE_CDN/vuetify@3/dist/vuetify.min.css"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_CSS/vuetify.min.css" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vuetify.min.css (Vuetify 3 styles) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Vuetify 3 CSS${NC}"
    exit 1
fi

# Step 8: Download Socket.IO Client 4
echo -e "${BLUE}Step 8: Downloading Socket.IO Client 4...${NC}"
curl -fsSL -o "$VENDOR_JS/socket.io.js" "$VUE_CDN/socket.io-client@4/dist/socket.io.min.js"
if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$VENDOR_JS/socket.io.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded socket.io.js (Socket.IO Client 4) - $SIZE${NC}"
else
    echo -e "${RED}✗ Failed to download Socket.IO Client 4${NC}"
    exit 1
fi

# Step 9: Check for vue-multiselect v3
echo -e "${BLUE}Step 9: Checking vue-multiselect v3 availability...${NC}"
MULTISELECT_URL="$UNPKG_CDN/vue-multiselect@3/dist/vue-multiselect.min.js"
if curl --output /dev/null --silent --head --fail "$MULTISELECT_URL"; then
    curl -fsSL -o "$VENDOR_JS/vue-multiselect.js" "$MULTISELECT_URL"
    SIZE=$(ls -lh "$VENDOR_JS/vue-multiselect.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vue-multiselect.js (v3) - $SIZE${NC}"
else
    echo -e "${BLUE}⚠ vue-multiselect v3 IIFE build not available on CDN${NC}"
    echo -e "${BLUE}  Will use Vuetify v-autocomplete as alternative${NC}"
fi

# Step 10: Check for vue-chartjs v4
echo -e "${BLUE}Step 10: Checking vue-chartjs v4 availability...${NC}"
CHARTJS_URL="$UNPKG_CDN/vue-chartjs@4/dist/vue-chartjs.umd.min.js"
if curl --output /dev/null --silent --head --fail "$CHARTJS_URL"; then
    curl -fsSL -o "$VENDOR_JS/vue-chartjs.js" "$CHARTJS_URL"
    SIZE=$(ls -lh "$VENDOR_JS/vue-chartjs.js" | awk '{print $5}')
    echo -e "${GREEN}✓ Downloaded vue-chartjs.js (v4) - $SIZE${NC}"
else
    echo -e "${BLUE}⚠ vue-chartjs v4 IIFE build not available on CDN${NC}"
    echo -e "${BLUE}  Will use direct Chart.js integration as alternative${NC}"
fi

echo ""
echo -e "${GREEN}=== Download Complete ===${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: ls -lh $VENDOR_JS"
echo "2. Run: ls -lh $VENDOR_CSS"
echo "3. Compare file sizes with backups in $BACKUP_JS"
echo "4. Test app loads without errors (no component changes yet)"
echo "5. Proceed to task-3.6 (App Initialization)"