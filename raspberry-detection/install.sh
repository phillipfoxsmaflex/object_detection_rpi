#!/bin/bash

# Farben für Ausgaben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging-Funktion
log() {
    echo -e "${GREEN}[+] $1${NC}"
}

error() {
    echo -e "${RED}[!] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Prüfe, ob das Script als root ausgeführt wird
if [ "$EUID" -ne 0 ]; then 
    error "Bitte führe das Script als root aus (sudo ./install.sh)"
fi

# Aktuelles Verzeichnis speichern
PROJECT_DIR=$(pwd)

# 1. System-Pakete aktualisieren
log "Aktualisiere System-Pakete..."
apt-get update || error "Konnte System-Pakete nicht aktualisieren"
apt-get upgrade -y || warning "Einige Pakete konnten nicht aktualisiert werden"

# 2. Benötigte System-Pakete installieren
log "Installiere benötigte System-Pakete..."
apt-get install -y \
    python3-venv \
    python3-picamera2 \
    mosquitto \
    mosquitto-clients \
    git \
    wget || error "Konnte benötigte Pakete nicht installieren"

# 3. MQTT-Broker aktivieren und starten
log "Konfiguriere MQTT-Broker..."
systemctl enable mosquitto
systemctl start mosquitto

# 4. Kamera aktivieren
log "Aktiviere Raspberry Pi Kamera..."
raspi-config nonint do_camera 0

# 5. Projekt-Struktur erstellen
log "Erstelle Projekt-Struktur..."
mkdir -p $PROJECT_DIR/{config,models,src}

# 6. YOLO-Modell herunterladen
log "Lade YOLO-Modell herunter..."
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O $PROJECT_DIR/models/yolov8n.pt || error "Konnte YOLO-Modell nicht herunterladen"

# 7. Virtuelle Umgebung erstellen
log "Erstelle virtuelle Python-Umgebung..."
python3 -m venv $PROJECT_DIR/venv --system-site-packages 
source $PROJECT_DIR/venv/bin/activate

# 8. Python-Pakete installieren
log "Installiere Python-Pakete..."
pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt || error "Konnte Python-Pakete nicht installieren"

# 9. Initiale Konfiguration erstellen
log "Erstelle initiale Konfiguration..."
cat > $PROJECT_DIR/config/settings.json << EOL
{
    "mqtt_broker": "localhost",
    "mqtt_port": 1883,
    "mqtt_topic": "detections",
    "model_path": "models/yolov8n.pt",
    "conf_threshold": 0.25
}
EOL

# 10. Berechtigungen setzen
log "Setze Berechtigungen..."
chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR
usermod -a -G video $SUDO_USER
chmod +x $PROJECT_DIR/src/*.py

# 11. Erstelle Start-Script
log "Erstelle Start-Script..."
cat > $PROJECT_DIR/start.sh << EOL
#!/bin/bash
#!/bin/bash
source venv/bin/activate
sudo env PATH=$PATH VIRTUAL_ENV=$VIRTUAL_ENV python src/app.py
EOL
chmod +x $PROJECT_DIR/start.sh

log "Installation abgeschlossen!"
log "Du kannst die Anwendung mit './start.sh' starten"
warning "Bitte starte den Raspberry Pi neu, damit alle Änderungen wirksam werden"

# Frage nach Neustart
read -p "Möchtest du den Raspberry Pi jetzt neu starten? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]
then
    log "System wird neu gestartet..."
    reboot
fi