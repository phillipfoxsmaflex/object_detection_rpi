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
USER=${SUDO_USER:-$USER}
GROUP=$(id -gn $USER)

# 1. System-Pakete aktualisieren
log "Aktualisiere System-Pakete..."
apt-get update || error "Konnte System-Pakete nicht aktualisieren"
apt-get upgrade -y || warning "Einige Pakete konnten nicht aktualisiert werden"

# 2. Benötigte System-Pakete installieren
log "Installiere benötigte System-Pakete..."
apt-get install -y \
    python3-venv \
    python3-picamera2 \
    python3-opencv \
    mosquitto \
    mosquitto-clients \
    git \
    wget \
    v4l-utils \
    libcamera-tools || error "Konnte benötigte Pakete nicht installieren"

# 3. MQTT-Broker konfigurieren und starten
log "Konfiguriere MQTT-Broker..."
systemctl enable mosquitto
systemctl start mosquitto

# 4. Kamera aktivieren und konfigurieren
log "Aktiviere und konfiguriere Raspberry Pi Kamera..."
raspi-config nonint do_camera 0
raspi-config nonint do_legacy_camera 1

# Kamera-Berechtigungen setzen
usermod -a -G video $USER
usermod -a -G video www-data

# 5. Projekt-Struktur erstellen
log "Erstelle Projekt-Struktur..."
mkdir -p $PROJECT_DIR/{config,models,src,logs}

# 6. YOLO-Modell herunterladen
log "Lade YOLO-Modell herunter..."
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O $PROJECT_DIR/models/yolov8n.pt || error "Konnte YOLO-Modell nicht herunterladen"

# 7. Python-Umgebung einrichten
log "Erstelle virtuelle Python-Umgebung..."
python3 -m venv $PROJECT_DIR/venv
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

# 10. Start-Scripts erstellen
log "Erstelle Start-Scripts..."
# Haupt-Start-Script
cat > $PROJECT_DIR/start.sh << EOL
#!/bin/bash
source venv/bin/activate
sudo env PATH=\$PATH VIRTUAL_ENV=\$VIRTUAL_ENV python src/app.py
EOL
chmod +x $PROJECT_DIR/start.sh

# Debug-Start-Script
cat > $PROJECT_DIR/start_debug.sh << EOL
#!/bin/bash
source venv/bin/activate
sudo env PATH=\$PATH VIRTUAL_ENV=\$VIRTUAL_ENV python src/app.py 2>&1 | tee logs/debug.log
EOL
chmod +x $PROJECT_DIR/start_debug.sh

# Kamera-Test-Script
cat > $PROJECT_DIR/test_camera.sh << EOL
#!/bin/bash
source venv/bin/activate
python src/test_camera.py
EOL
chmod +x $PROJECT_DIR/test_camera.sh

# 11. Systemd Service erstellen (optional)
log "Erstelle Systemd Service..."
cat > /etc/systemd/system/object-detection.service << EOL
[Unit]
Description=Object Detection Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 12. Berechtigungen setzen
log "Setze Berechtigungen..."
chown -R $USER:$GROUP $PROJECT_DIR
chmod -R 755 $PROJECT_DIR/src
chmod 644 $PROJECT_DIR/config/settings.json
chmod 644 /etc/systemd/system/object-detection.service

# 13. Systemd Service aktivieren (optional)
log "Aktiviere Systemd Service..."
systemctl daemon-reload
systemctl enable object-detection.service

# 14. Erstelle Readme
cat > $PROJECT_DIR/README.md << EOL
# Object Detection App

## Installation
Die Installation wurde automatisch durch das install.sh Script durchgeführt.

## Starten der Anwendung
Es gibt verschiedene Möglichkeiten, die Anwendung zu starten:

1. Normaler Start:
   \`\`\`bash
   ./start.sh
   \`\`\`

2. Start mit Debug-Output:
   \`\`\`bash
   ./start_debug.sh
   \`\`\`

3. Kamera-Test:
   \`\`\`bash
   ./test_camera.sh
   \`\`\`

4. Als Service:
   \`\`\`bash
   sudo systemctl start object-detection
   \`\`\`

## Zugriff auf die Web-Oberfläche
Die Web-Oberfläche ist erreichbar unter:
http://[raspberry-pi-ip]:7860

## Logs
Die Logs befinden sich im \`logs\` Verzeichnis.
EOL

log "Installation abgeschlossen!"
log "Du kannst die Anwendung wie folgt starten:"
log "1. Normal:        ./start.sh"
log "2. Mit Debug:     ./start_debug.sh"
log "3. Kamera-Test:   ./test_camera.sh"
log "4. Als Service:   sudo systemctl start object-detection"

warning "Bitte starte den Raspberry Pi neu, damit alle Änderungen wirksam werden"

# Frage nach Neustart
read -p "Möchtest du den Raspberry Pi jetzt neu starten? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]
then
    log "System wird neu gestartet..."
    reboot
fi
