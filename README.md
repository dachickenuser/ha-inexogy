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

## OAuth1 setup (UI flow)

1. Inexogy uses OAuth 1.0 (HMAC-SHA1). You will need a Consumer Key and Consumer Secret from Inexogy (or the partner portal).
2. Add the integration in Home Assistant and enter the `consumer_key` and `consumer_secret` when prompted.
3. The flow will show an `authorize_url`. Open it in your browser, sign in to the Inexogy portal and approve the app.
4. Copy the verifier / PIN shown by Inexogy and paste it back into the config flow.
5. After successful authentication the integration will fetch accessible meters and create sensors.

Notes:
- If you are unsure how to obtain `consumer_key`/`consumer_secret`, contact Inexogy support or check the partner portal. Some deployments expose a `/oauth1/consumer_token` endpoint; this integration expects you to provide the consumer credentials up-front.
- The integration sets the HTTP `Accept` header to include `text/plain` so human-readable error messages from the API are returned when present.

## Polling interval option

The integration polls the API for the latest reading. The default polling interval is 60 seconds. You can change this per-config-entry in the integration options (`update_interval` in seconds).

## API payload notes

Example `last_reading` payload (simplified):

```json
{
   "meterId": "abc123",
   "values": {
      "power": 1234,
      "energy": 456789,        // total Wh
      "energyOut": 12345       // exported Wh
   },
   "timestamp": "2025-12-29T12:00:00Z"
}
```

- `power` is in Watts.
- `energy` and `energyOut` are provided in Watt-hours (Wh) and are converted to kWh in the sensors (divide by 1000).

If you find different field names or units in your account, please open an issue with an example payload.
