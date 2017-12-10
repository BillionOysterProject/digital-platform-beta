'use strict';

$(function(){
    var App = Stapes.subclass({
        constructor: function() {
        },

        authenticate: function(el) {
            var form = $(el);
            var username = form.find('input[name="username"]').val();
            var password = form.find('input[name="password"]').val();

            $.ajax({
                url:    form.attr('action'),
                method: form.attr('method'),
                data: {
                    'username': username,
                    'password': password,
                },
                success: function() {
                    window.location = '/';
                },
                error: function(data) {
                    console.error('Failed', data);
                },
            })

            return false;
        },
    });

    var bop = new App();
});
