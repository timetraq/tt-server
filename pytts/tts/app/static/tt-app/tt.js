/* Creating namespaces */

(function (namespace, $) {
    'use strict';

    var local = {};

    local.registrationDialog = function () {
        BootstrapDialog.show({
            title: 'Registration',
            message: $('<div></div>').load('dialogs/registration.xhtml')
        });
    };

    $(window).ready(function () {
        local.registrationDialog();
    });

})(window.tts = window.tts || {}, jQuery);