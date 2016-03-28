/* Creating namespaces */

(function (namespace, $) {
    'use strict';

    var local = {};

    namespace.ajaxSettings = {
        method: 'POST',
        async: true,
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    };

    namespace.registrationDialog = function () {
        BootstrapDialog.show({
            title: 'Registration',
            message: $('<div></div>').load('dialogs/registration.xhtml'),
            onshown: function () {
                window.tts.registration.init(this);
            }
        });
    };

    local.init = function () {
        $('*[data-formaction="registrationForm"]').on('click', function () {
            namespace.registrationDialog();
        });
    };

    $(window).ready(function () {
        local.init();
    });

})(window.tts = window.tts || {}, jQuery);