#!/bin/bash
# verify-vendor-files.sh
# Verifies Vue 3 + Vuetify 3 vendor files and documents sizes
# Task: task-3.5

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paths
VENDOR_JS="src/baseweb/static/vendor/js"
VENDOR_CSS="src/baseweb/static/vendor/css"
BACKUP_JS="src/baseweb/static/vendor/js.backup"
BACKUP_CSS="src/baseweb/static/vendor/css.backup"

echo -e "${BLUE}=== Vendor File Verification ===${NC}"
echo ""

# Function to check file exists and get size
check_file() {
    local file=$1
    local expected=$2

    if [ -f "$file" ]; then
        local size=$(ls -lh "$file" | awk '{print $5}')
        local filename=$(basename "$file")

        # Check file header for version
        local version="unknown"
        case $filename in
            vue.js)
                version=$(grep -o "Vue.js v[0-9.]*" "$file" | head -1 || echo "Vue 3.x")
                ;;
            vue-router.js)
                version=$(grep -o "vue-router v[0-9.]*" "$file" | head -1 || echo "Vue Router 4.x")
                ;;
            vuex.js)
                version=$(grep -o "vuex v[0-9.]*" "$file" | head -1 || echo "Vuex 4.x")
                ;;
            vuetify.js)
                version=$(grep -o "Vuetify v[0-9.]*" "$file" | head -1 || echo "Vuetify 3.x")
                ;;
            socket.io.js)
                version=$(grep -o "Socket.IO v[0-9.]*" "$file" | head -1 || echo "Socket.IO 4.x")
                ;;
        esac

        echo -e "${GREEN}✓${NC} $filename ($version) - ${size}"
        return 0
    else
        echo -e "${YELLOW}✗${NC} $expected - NOT FOUND"
        return 1
    fi
}

# Check JavaScript files
echo -e "${BLUE}JavaScript Files:${NC}"
echo "------------------------------------------------------------"
check_file "$VENDOR_JS/vue.js" "Vue 3" || true
check_file "$VENDOR_JS/vue-router.js" "Vue Router 4" || true
check_file "$VENDOR_JS/vuex.js" "Vuex 4" || true
check_file "$VENDOR_JS/vuetify.js" "Vuetify 3" || true
check_file "$VENDOR_JS/socket.io.js" "Socket.IO Client 4" || true

# Check optional files
if [ -f "$VENDOR_JS/vue-multiselect.js" ]; then
    echo -e "${GREEN}✓${NC} vue-multiselect.js (v3) - $(ls -lh "$VENDOR_JS/vue-multiselect.js" | awk '{print $5}')"
else
    echo -e "${BLUE}○${NC} vue-multiselect.js - Not installed (will use Vuetify alternative)"
fi

if [ -f "$VENDOR_JS/vue-chartjs.js" ]; then
    echo -e "${GREEN}✓${NC} vue-chartjs.js (v4) - $(ls -lh "$VENDOR_JS/vue-chartjs.js" | awk '{print $5}')"
else
    echo -e "${BLUE}○${NC} vue-chartjs.js - Not installed (will use Chart.js directly)"
fi

echo ""
echo -e "${BLUE}CSS Files:${NC}"
echo "------------------------------------------------------------"
check_file "$VENDOR_CSS/vuetify.min.css" "Vuetify 3 CSS" || true

echo ""

# Compare with backups if they exist
if [ -d "$BACKUP_JS" ] && [ "$(ls -A $BACKUP_JS 2>/dev/null)" ]; then
    echo -e "${BLUE}Size Comparison (Old vs New):${NC}"
    echo "------------------------------------------------------------"

    for file in vue.js vue-router.js vuex.js vuetify.js; do
        if [ -f "$BACKUP_JS/$file" ] && [ -f "$VENDOR_JS/$file" ]; then
            old_size=$(ls -lh "$BACKUP_JS/$file" | awk '{print $5}')
            new_size=$(ls -lh "$VENDOR_JS/$file" | awk '{print $5}')

            # Extract version info
            old_version="Vue 2.x"
            new_version="Vue 3.x"
            case $file in
                vue.js)
                    old_version=$(grep -o "Vue.js v[0-9.]*" "$BACKUP_JS/$file" 2>/dev/null | head -1 || echo "v2.x")
                    new_version=$(grep -o "Vue.js v[0-9.]*" "$VENDOR_JS/$file" 2>/dev/null | head -1 || echo "v3.x")
                    ;;
                vue-router.js)
                    old_version=$(grep -o "vue-router v[0-9.]*" "$BACKUP_JS/$file" 2>/dev/null | head -1 || echo "v3.x")
                    new_version=$(grep -o "vue-router v[0-9.]*" "$VENDOR_JS/$file" 2>/dev/null | head -1 || echo "v4.x")
                    ;;
                vuex.js)
                    old_version=$(grep -o "vuex v[0-9.]*" "$BACKUP_JS/$file" 2>/dev/null | head -1 || echo "v3.x")
                    new_version=$(grep -o "vuex v[0-9.]*" "$VENDOR_JS/$file" 2>/dev/null | head -1 || echo "v4.x")
                    ;;
                vuetify.js)
                    old_version=$(grep -o "Vuetify v[0-9.]*" "$BACKUP_JS/$file" 2>/dev/null | head -1 || echo "v2.x")
                    new_version=$(grep -o "Vuetify v[0-9.]*" "$VENDOR_JS/$file" 2>/dev/null | head -1 || echo "v3.x")
                    ;;
            esac

            printf "%-20s %10s  (%s)  →  %10s  (%s)\n" "$file" "$old_size" "$old_version" "$new_size" "$new_version"
        fi
    done

    echo ""

    # Calculate total size difference
    echo -e "${BLUE}Total Size Summary:${NC}"
    old_total=$(du -sh "$BACKUP_JS" 2>/dev/null | awk '{print $1}')
    new_total=$(du -sh "$VENDOR_JS" 2>/dev/null | awk '{print $1}')
    echo "  Old total: $old_total"
    echo "  New total: $new_total"
fi

echo ""
echo -e "${BLUE}Backup Locations:${NC}"
echo "  JavaScript: $BACKUP_JS/"
echo "  CSS:        $BACKUP_CSS/"
echo ""

# Check for global variable patterns
echo -e "${BLUE}Global Variable Check:${NC}"
echo "------------------------------------------------------------"
if grep -q "global.Vue = " "$VENDOR_JS/vue.js" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Vue 3 global build detected (IIFE format)"
else
    echo -e "${YELLOW}⚠${NC} Vue 3 may not be IIFE build"
fi

if grep -q "global.VueRouter = " "$VENDOR_JS/vue-router.js" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Vue Router 4 global build detected (IIFE format)"
else
    echo -e "${YELLOW}⚠${NC} Vue Router 4 may not be IIFE build"
fi

if grep -q "global.Vuex = " "$VENDOR_JS/vuex.js" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Vuex 4 global build detected (IIFE format)"
else
    echo -e "${YELLOW}⚠${NC} Vuex 4 may not be IIFE build"
fi

if grep -q "global.Vuetify = " "$VENDOR_JS/vuetify.js" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Vuetify 3 global build detected"
else
    echo -e "${YELLOW}⚠${NC} Vuetify 3 may not be global build"
fi

if grep -q "io\(" "$VENDOR_JS/socket.io.js" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Socket.IO client detected"
else
    echo -e "${YELLOW}⚠${NC} Socket.IO client may not be correct build"
fi

echo ""
echo -e "${GREEN}=== Verification Complete ===${NC}"
echo ""
echo "Next step: Test app loads without modifying components"