/* The rules */

(function (namespace) {

    namespace.user = /^[A-Za-z0-9]{3,32}$/;
    namespace.password = /^.{8,255}$/;

})(window.tts.rules = window.tts.rules || {});
