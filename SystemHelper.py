# Update package list
sudo apt update && sudo apt upgrade -y

# Install dependencies utama
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Install Python dependencies tambahan
sudo apt install -y python3-dev python3-setuptools python3-wheel

# Install Cython (diperlukan untuk Kivy)
pip3 install --user cython

# Install Buildozer
pip3 install --user buildozer



# Clean previous builds (opsional)
buildozer distclean

# Update dependencies
buildozer update

# Build APK debug
buildozer android debug

# Atau build APK release (untuk distribusi)
buildozer android release
