/* Registration Form Lib */

(function (namespace, $) {
    'use strict';

    var local = {};

    local.states = {};

    local.getToken = function (id, form) {
        $.getJSON('/api/v1.0/registration/prepare').done(
            function (json) {
                local.states[id].token = json.token;
                local.states[id].registration_key = json.registration_key;
                local.states[id].state = 1;
            }
        ).fail(function() {
            $(form).find('input').prop('disabled', true);
            $(form).find('.well').remove();
            var errorMessage = $('<div></div>').attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Failed to get a token for registration.');
            $(form).prepend(errorMessage);
            delete local.states[id];
        });
    };

    local.checkUsername = function (id, form) {
        var usernameField = $(form).find('input#formlib_registration_username');
        var username = $(usernameField).val();
        var div = $(usernameField).parent();
        $(form).find('div[data-fieldref="' + $(usernameField).attr('id') + '"]').remove();
        $(div).removeClass('has-warning').removeClass('has-error').removeClass('has-success');
        $(div).find('span.form-control-feedback').removeClass('glyphicon-warning-sign').removeClass('glyphicon-exclamation-sign').removeClass('glyphicon-ok');
        $(div).find('span#formlib_registration_usernameStatus').text('(processing)');
        if (!tts.rules.user.test(username)) {
            $('<div></div>').attr('data-fieldref', $(usernameField).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Username invalid').insertBefore($(div));
            $(div).addClass('has-error');
            $(div).find('span#formlib_registration_usernameStatus').text('(error)');
            $(div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
            return;
        }
        $(usernameField).prop('disabled', true);
        var requestData = $.extend({}, {
            data: JSON.stringify({
                username: username,
                registration_key: local.states[id].registration_key,
                token: local.states[id].token
            })
        }, tts.ajaxSettings);
        $.ajax('/api/v1.0/registration/choose_username', requestData).done(
            function (json) {
                local.states[id].registration_key = json.registration_key;
                local.states[id].token = json.token;
                if (json.username_message != 'username_available') {
                    $('<div></div>').attr('data-fieldref', $(usernameField).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Username invalid: ' + json.username_message).insertBefore($(div));
                    $(div).addClass('has-error');
                    $(div).find('span#formlib_registration_usernameStatus').text('(error)');
                    $(div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
                    $(usernameField).prop('disabled', false);
                    return;
                }
                $(div).addClass('has-success');
                $(div).find('span#formlib_registration_usernameStatus').text('(ok)');
                $(div).find('span.form-control-feedback').addClass('glyphicon-ok');
                local.states[id].state = 2;
                $('<div></div>').load('dialogs/registration_passwords.xhtml', function() {
                    $(form).find('input#formlib_registration_password1').focus();
                }).insertBefore($(form).find('button[type="submit"]'));
            }
        ).fail(
            function (jqXHR, textStatus) {
                $(form).find('input').prop('disabled', true);
                $('<div></div>').attr('data-fieldref', $(usernameField).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Error handling request: ' + textStatus).insertBefore($(div));
                $(div).addClass('has-error');
                $(div).find('span#formlib_registration_usernameStatus').text('(error)');
                $(div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
            }
        );
    };

    local.checkPasswords = function (id, form) {
        var p1 = $(form).find('input#formlib_registration_password1');
        var p2 = $(form).find('input#formlib_registration_password2');
        // Remove old error messages
        var p1div = $(p1).parent();
        var p2div = $(p2).parent();
        $([p1div, p2div]).each(function(index, div) {
            $(div).removeClass('has-warning').removeClass('has-error').removeClass('has-success');
            $(div).find('span.form-control-feedback').removeClass('glyphicon-warning-sign').removeClass('glyphicon-exclamation-sign').removeClass('glyphicon-ok');
            $(div).find('span#' + $(div).find('input').attr('aria-describedby')).text('(processing)');
            $(form).find('div[data-fieldref="' + $(div).find('input').attr('id') + '"]').remove();
        });
        if ($(p1).is(':focus')) {
            if (!tts.rules.password.test(p1.val())) {
                // Mark p1 with error
                $('<div></div>').attr('data-fieldref', $(p1).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Password invalid').insertBefore($(p1div));
                $(p1div).addClass('has-error');
                $(p1div).find('span#'+ $(p1div).find('input').attr('aria-describedby')).text('(error)');
                $(p1div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
                return;
            }
            $(p1div).addClass('has-success');
            $(p1div).find('span#'+ $(p1div).find('input').attr('aria-describedby')).text('(ok)');
            $(p1div).find('span.form-control-feedback').addClass('glyphicon-ok');
            $(p2div).addClass('has-warning');
            $(p2div).find('span#'+ $(p2div).find('input').attr('aria-describedby')).text('(warning)');
            $(p2div).find('span.form-control-feedback').addClass('glyphicon-warning-sign');
            $(p2).focus();
        }
        else if ($(p2).is(':focus')) {
            if (!tts.rules.password.test($(p1).val())) {
                // Mark p1 with error
                $('<div></div>').attr('data-fieldref', $(p1).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Password invalid').insertBefore($(p1div));
                $(p1div).addClass('has-error');
                $(p1div).find('span#'+ $(p1div).find('input').attr('aria-describedby')).text('(error)');
                $(p1div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
                $(p1).focus();
                return;
            }
            else {
                $(p1div).addClass('has-success');
                $(p1div).find('span#'+ $(p1div).find('input').attr('aria-describedby')).text('(ok)');
                $(p1div).find('span.form-control-feedback').addClass('glyphicon-ok');
            }
            if ($(p1).val() != $(p2).val()) {
                // Mark p2 with error
                $('<div></div>').attr('data-fieldref', $(p2).attr('id')).attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Passwords do not match').insertBefore($(p2div));
                $(p2div).addClass('has-error');
                $(p2div).find('span#'+ $(p1div).find('input').attr('aria-describedby')).text('(error)');
                $(p2div).find('span.form-control-feedback').addClass('glyphicon-exclamation-sign');
                return;
            }
            $(p2div).addClass('has-success');
            $(p2div).find('span#'+ $(p2div).find('input').attr('aria-describedby')).text('(ok)');
            $(p2div).find('span.form-control-feedback').addClass('glyphicon-ok');
            $(p1).prop('disabled', true);
            $(p2).prop('disabled', true);
            var requestData = $.extend({}, {
                data: JSON.stringify({
                    password: $(p1).val(),
                    registration_key: local.states[id].registration_key,
                    token: local.states[id].token
                })
            }, tts.ajaxSettings);
            $('<hr />').insertBefore($(form).find('button[type="submit"]'));
            $.ajax('/api/v1.0/registration/set_password', requestData).done(
                function (json) {
                    var msgDiv = $('<div></div>').attr('role', 'alert').addClass('alert');
                    if (json.error) {
                        $(msgDiv).addClass('alert-danger').text('Registration failed: [' + json.error.code + '] ' + json.error.message);
                    }
                    else {
                        $(msgDiv).addClass('alert-success').text('Registration successful');
                    }
                    $(msgDiv).insertBefore($(form).find('button[type="submit"]'));
                }
            ).fail(
                function (jqXHR, textStatus) {
                    $('<div></div>').attr('role', 'alert').addClass('alert').addClass('alert-danger').text('Registration failed: ' + textStatus).insertBefore($(form).find('button[type="submit"]'));
                }
            ).always(
                function () {
                    var oldSubmitButton = $(form).find('button[type="submit"]');
                    $('<hr />').insertBefore($(oldSubmitButton));
                    var closeButton = $('<button><span class="glyphicon glyphicon-remove"></span> Close</button>').addClass('btn').addClass('btn-default');
                    $(closeButton).insertBefore($(oldSubmitButton));
                    $(oldSubmitButton).remove();
                    $(closeButton).click(function () {
                        BootstrapDialog.dialogs[id].close();
                    });
                }
            );
        }
    };

    local.nextStep = function (id, form) {
        if (!(local.states[id])) {
            window.console.error('No State saved for Multi-State Form with the ID ' + id);
            return;
        }
        ({
            0: local.getToken,
            1: local.checkUsername,
            2: local.checkPasswords
        })[local.states[id].state](id, form);
    };

    local.prepareForm = function (id, form) {
        local.states[id] = { state: 0 };
        $(form).on('submit', function (event) {
            event.preventDefault();
            event.stopPropagation();
            local.nextStep(id, form);
            return false;
        });
        local.nextStep(id, form);
    };

    namespace.init = function (that) {
        local.prepareForm(that.id, $(that.message).find('form'));
    };

})(window.tts.registration = window.tts.registration || {}, jQuery);
