# Inexogy Smart Meter for Home Assistant

Dieses Custom Component bindet Inexogy-Zähler per OAuth1 in Home Assistant ein.

## Installation

1. Repository nach GitHub pushen, z. B. `https://github.com/dachickenuser/ha-inexogy`
2. In Home Assistant → HACS → Integrationen → Custom repositories:
   - URL: `https://github.com/dachickenuser/ha-inexogy`
   - Typ: Integration
3. Integration in HACS installieren
4. Home Assistant neu starten
5. Einstellungen → Geräte & Dienste → Integration hinzufügen → "Inexogy"

## Konfiguration (UI)

1. Consumer Key und Consumer Secret eintragen (von Inexogy/Discovergy erhalten)
2. Im zweiten Schritt erscheint eine URL (`authorize_url`)
3. Link im Browser öffnen, bei Inexogy einloggen, Verifier/PIN kopieren
4. Verifier im zweiten Schritt eintragen
5. Nach erfolgreichem Test werden Meter automatisch als Sensoren angelegt:

- `<Name> Power` (W)
- `<Name> Energy Import` (kWh)
- `<Name> Energy Export` (kWh)
