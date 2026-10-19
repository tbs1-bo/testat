# flask-dance bleibt, oauth2-proxy verworfen

Geprüft wurde, ob [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy/) die OAuth-Anbindung per `flask-dance` ersetzen kann ([#3](https://github.com/tbs1-bo/testat/issues/3), TODO aus [c00fe7c](https://github.com/tbs1-bo/testat/commit/c00fe7c)). Verworfen: Die Auth läuft stabil, und ein weiterer Proxy würde die ohnehin lange Kette (nginx → Apache → App) um eine zusätzliche Indirektion verlängern.
