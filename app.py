import os
import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "").strip()
FOOTBALL_BASE = "https://v3.football.api-sports.io"

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.get("/api/status")
def status():
    return jsonify({"ok": True, "football_api_configured": bool(API_FOOTBALL_KEY), "free": True})

@app.get("/api/fixtures")
def fixtures():
    if not API_FOOTBALL_KEY:
        return jsonify({"error": "Les données réelles ne sont pas encore activées. L'application est gratuite, mais il faut ajouter une clé API-Football dans les variables d'environnement pour charger les matchs."}), 503
    mode = request.args.get("mode", "today")
    params = {"live": "all"} if mode == "live" else {"date": request.args.get("date", __import__("datetime").date.today().isoformat()), "timezone": "Africa/Abidjan"}
    try:
        r = requests.get(FOOTBALL_BASE + "/fixtures", headers={"x-apisports-key": API_FOOTBALL_KEY}, params=params, timeout=20)
        r.raise_for_status()
        return jsonify(r.json())
    except requests.RequestException:
        return jsonify({"error": "Impossible de récupérer les matchs pour le moment. Réessaie plus tard."}), 503

@app.get("/api/<kind>")
def football_detail(kind):
    if kind not in ("predictions", "odds", "statistics"):
        return jsonify({"error": "Endpoint inconnu."}), 404
    if not API_FOOTBALL_KEY:
        return jsonify({"error": "Les données de football ne sont pas encore configurées."}), 503
    fixture = request.args.get("fixture", "")
    if not fixture.isdigit():
        return jsonify({"error": "Identifiant de match invalide."}), 400
    path = {"predictions": "/predictions", "odds": "/odds", "statistics": "/fixtures/statistics"}[kind]
    try:
        r = requests.get(FOOTBALL_BASE + path, headers={"x-apisports-key": API_FOOTBALL_KEY}, params={"fixture": fixture}, timeout=20)
        r.raise_for_status()
        return jsonify(r.json())
    except requests.RequestException:
        return jsonify({"error": "Données indisponibles pour ce match."}), 503

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")), debug=False)
