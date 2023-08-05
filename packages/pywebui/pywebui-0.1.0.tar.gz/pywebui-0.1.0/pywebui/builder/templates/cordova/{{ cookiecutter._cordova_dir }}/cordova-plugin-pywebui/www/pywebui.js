var exec = require('cordova/exec')

window.cordova_pywebui_call = function(request, success, error) {
  exec(
    success,
    error,
    'PyWebUI',
    'call',
    [request]
  );
}

module.exports = window.cordova_pywebui_call;