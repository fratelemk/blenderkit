BASE_URL=https://download.blender.org/release/
ARCH=$(uname -m)

echo "You're about to install Blender."

MAJOR_VERSION=$(curl -s "$BASE_URL" \
	| grep -oE 'Blender[0-9]+\.[0-9]+' \
	| sort -V \
	| uniq \
	| tail -n1)

read -p "Do you want to proceed with the latest version? ($MAJOR_VERSION) (y/n): " choice

if [[ $choice == "y" || $choice == "Y" ]]; then
	FULL_VERSION=$(curl -s "${BASE_URL}${MAJOR_VERSION}/" \
		| grep -oE 'blender-[0-9]+\.[0-9]+\.[0-9]+' \
		| sort -V \
		| uniq \
		| tail -n1 \
		| grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
else
	read -p "Enter Blender major version (e.g. 5.1): " INPUT_VERSION
	MAJOR_VERSION="Blender${INPUT_VERSION}"

	MINOR_VERSIONS=$(curl -s "${BASE_URL}${MAJOR_VERSION}/" \
		| grep -oE 'blender-[0-9]+\.[0-9]+\.[0-9]+' \
		| sort -V \
		| uniq \
		| grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

	COUNT=$(echo "$MINOR_VERSIONS" | wc -l | tr -d ' ')

	if [[ $COUNT -gt 1 ]]; then
		echo "Available versions:"
		echo "$MINOR_VERSIONS" | nl -ba
		read -p "Select a version number: " VERSION_NUM
		FULL_VERSION=$(echo "$MINOR_VERSIONS" | sed -n "${VERSION_NUM}p")
	else
		FULL_VERSION="$MINOR_VERSIONS"
	fi
fi

DOWNLOAD_URL="${BASE_URL}${MAJOR_VERSION}/blender-${FULL_VERSION}-macos-${ARCH}.dmg"
echo "Downloading Blender ${FULL_VERSION} from ${DOWNLOAD_URL}..."
curl -L -O "$DOWNLOAD_URL"
