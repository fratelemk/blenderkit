BASE_URL=https://flamenco.blender.org/downloads/
ARCH=$(uname -m)
VERSION=3.8.5

FILENAME="flamenco-${VERSION}-macos-${ARCH}.tar.gz"
DOWNLOAD_URL="${BASE_URL}${FILENAME}"

echo "Downloading Flamenco ${VERSION} from ${DOWNLOAD_URL}..."
curl -L -O "$DOWNLOAD_URL"

echo "Unarchiving ${FILENAME}..."
tar -xzf "$FILENAME"
rm "$FILENAME"

EXTRACT_DIR="flamenco-${VERSION}-macos-${ARCH}"

read -p "Is this installation intended for a render node? (y/n): " render_node
if [[ $render_node == "y" || $render_node == "Y" ]]; then
	rm "${EXTRACT_DIR}/flamenco-manager"
fi
