# Update dan install dependencies
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev python3-dev python3-setuptools python3-wheel python3-venv python3-full


# Buat virtual environment
python3 -m venv ~/buildozer_env

# Aktifkan virtual environment
source ~/buildozer_env/bin/activate

# Install buildozer di virtual environment
pip install buildozer cython

# Verifikasi install
which buildozer
buildozer --version

# Tambahkan ke ~/.bashrc
echo 'export PATH=$PATH:~/buildozer_env/bin' >> ~/.bashrc
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc

# Reload environment
source ~/.bashrc

# Masuk ke direktori project
cd ~/Desktop/CODING\ ERA/Android\ Multi

# Pastikan virtual environment aktif
source ~/buildozer_env/bin/activate

# Build APK
buildozer android debug

# Install semua yang diperlukan sekaligus
sudo apt update && sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev python3-dev python3-setuptools python3-wheel python3-venv python3-full && python3 -m venv ~/buildozer_env && source ~/buildozer_env/bin/activate && pip install buildozer cython

# Cek apakah buildozer sudah terinstall
which buildozer

# Cek versi
buildozer --version

# Cek PATH
echo $PATH

# Coba install dengan pipx
sudo apt install pipx
pipx install buildozer

# Atau install global dengan override
pip3 install --user --break-system-packages buildozer
