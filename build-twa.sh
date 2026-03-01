#!/bin/bash

# FidaMano TWA Build Script for Google Play Store
# This script builds a Trusted Web Activity (TWA) for FidaMano

set -e

echo "🚀 Building FidaMano TWA for Google Play Store..."

# Check if required tools are installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install npm first."
    exit 1
fi

# Install bubblewrap CLI if not installed
if ! command -v bubblewrap &> /dev/null; then
    echo "📦 Installing bubblewrap CLI..."
    npm install -g @bubblewrap/cli
fi

# Create output directory
mkdir -p build
cd build

# Generate Android keystore if it doesn't exist
if [ ! -f "../android.keystore" ]; then
    echo "🔐 Generating Android keystore..."
    keytool -genkey -v -keystore ../android.keystore \
        -alias fidamano \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -dname "CN=FidaMano, OU=Development, O=FidaMano, L=Milan, ST=Italy, C=IT" \
        -storepass fidamano123 \
        -keypass fidamano123
fi

# Build TWA using bubblewrap
echo "🏗️ Building TWA..."

bubblewrap build \
    --manifest ../twa-config.json \
    --output fidamano-twa \
    --keystore ../android.keystore \
    --keystore-pass fidamano123 \
    --key-alias fidamano

echo "✅ TWA build completed successfully!"
echo ""
echo "📱 Generated files:"
echo "  - fidamano-twa.apk (for testing)"
echo "  - fidamano-twa.aab (for Google Play Store)"
echo ""
echo "📋 Next steps:"
echo "1. Test the APK: adb install fidamano-twa.apk"
echo "2. Upload the AAB to Google Play Console"
echo "3. Complete the store listing with screenshots and descriptions"
echo ""
echo "🔍 Requirements for Google Play Store:"
echo "- SSL certificate (HTTPS) for fidamano.com"
echo "- App icon 512x512px"
echo "- Feature graphic 1024x500px"
echo "- Screenshots (phone and tablet)"
echo "- Privacy policy URL"
echo "- Target audience and content rating"
