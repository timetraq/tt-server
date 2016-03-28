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
            title: '<b>Registration</b>',
            message: $('<div></div>').load('dialogs/registration.xhtml'),
            closeIcon: '<span class="glyphicon glyphicon-remove"></span>',
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