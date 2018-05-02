'use strict';

// return whether the input is null OR undefined
window.isEmpty = function(v) {
    if(v === null || v === undefined) {
        return true;
    }

    return false;
};

$(function(){
    Raven.config('https://5f7fe95584dc40f8adfd06ead1d1748c@sentry.io/1199998').install();

    Raven.context(function() {
        var App = Stapes.subclass({
            constructor: function() {
                this.setupAjaxIntercept();
                this.setupFormIntercept();
                this.setupTypeaheadHandlers();
            },

            setupAjaxIntercept: function() {
                $(document).ajaxError(function(res, xhr, settings) {
                    console.debug('args', arguments)
                    Raven.captureMessage('HTTP ' + res.status, {
                        'status':   res.status,
                        'payload':  (res.responseJSON || res.responseText),
                        'settings': settings,
                    });
                });
            },

            setupFormIntercept: function() {
                // prevent normal form submissions, we'll handle them here
                $('form').on('submit', function(e){
                    try {
                        var st = $(e.currentTarget).attr('data-form-type');

                        if(st === 'traditional' || st === 'custom') {
                            return;
                        }

                        this.submitForm(e);
                    } catch(e) {
                        this.notify('Form Error: ' + e.message, 'error');
                    }

                    e.preventDefault();
                }.bind(this));
            },

            submitForm: function(event){
                var form = $(event.target);
                var formEl = form.get(0);
                var url = '';

                if (formEl.action && formEl.action.length > 0) {
                    url = formEl.action;
                } else if (name = form.attr('name')) {
                    url = '/api/' + name;
                } else {
                    this.notify('Could not determine path to submit data to', 'error');
                    return;
                }

                var createNew = true;
                var record = {};

                $.each(form.serializeArray(), function(i, field) {
                    if(field.value == '' || field.value == '0'){
                        delete field['value'];
                    }


                    if(field.name == "_id"){
                        if(field.value){
                            createNew = false;
                        }

                        record['_id'] = field.value;
                    }else if(!isEmpty(field.value)){
                        record[field.name] = field.value;
                    }
                });

                $.ajax(url, {
                    method: (form.attr('method') || (createNew ? 'POST' : 'PUT')),
                    data:   record,
                    success: function(){
                        var redirectTo = '/';

                        if (form.data('redirect-to')) {
                            redirectTo = form.data('redirect-to');
                        } else if (form.attr('name')) {
                            redirectTo = '/' + form.attr('name');
                        }

                        location.href = redirectTo;
                    }.bind(this),
                    error: function(data) {
                        console.error('Form Error:', data);
                        this.showResponseError(data);
                    }.bind(this),
                })
            },

            // show a notification alert bubble
            notify: function(message, type, details, config){
                $.notify($.extend(details, {
                    'message': message,
                }), $.extend(config, {
                    'type': (type || 'info'),
                }));
            },

            // show a notification bubble for response errors
            showResponseError: function(response){
                this.notify(response.responseText, 'danger', {
                    'icon': 'fa fa-warning',
                    'title': '<b>' +
                        response.statusText + ' (HTTP '+response.status.toString()+')' +
                        '<br />' +
                    '</b>',
                });
            },

            setupTypeaheadHandlers: function() {
                // setup typeahead for fields that have it
                $('.typeahead').each(function(i, el){
                    el = $(el);

                    el.typeahead({
                        highlight: true,
                        async: true,
                    },{
                        limit: parseInt(el.data('typeahead-limit') || 9),
                        source: function(query, _, asyncResults){
                            var url = el.data('typeahead-url');
                            var field = el.data('typeahead-field');

                            if(url){
                                url = url.replace('{}', query.replace(/^\//, ''));

                                $.ajax(url, {
                                    success: function(data){
                                        if (field) {
                                            var results = [];

                                            $.each(data, function(i, value) {
                                                if ($.isPlainObject(value)) {
                                                    results.push(value[field]);
                                                }
                                            });

                                            asyncResults(results);
                                        } else {
                                            asyncResults(data);
                                        }
                                    }.bind(this),
                                    error: this.showResponseError.bind(this),
                                });
                            }
                        }.bind(this),
                    });
                }.bind(this));
            },

            genericMapClickHandler: function(map, layers) {
                return function(e) {
                    try {
                        var features = map.queryRenderedFeatures(e.point, {
                            "layers": layers,
                        });

                        if (!features.length) {
                            return;
                        }

                        var feature = features[0];

                        if (!feature.properties.description) {
                            feature.properties.description = '';

                            if (feature.properties.name) {
                                feature.properties.description += '<h1>' + feature.properties.name + '</h1>';
                            }

                            if (feature.properties.type) {
                                feature.properties.description += '<strong>' + feature.properties.type + '</strong>';
                            }
                        }

                        var currentPopup = new mapboxgl.Popup({ offset: [0, -15] })
                            .setLngLat(feature.geometry.coordinates)
                            .setHTML('<p>' + feature.properties.description + '</p>')
                            .setLngLat(feature.geometry.coordinates)
                            .addTo(map);
                    } catch(e) {
                        ;
                    }
                }
            },

            genericMapHoverHandler: function(map, layers) {
                return function(e) {
                    var features = map.queryRenderedFeatures(e.point, {
                        "layers": layers,
                    })

                    if (features.length) {
                        map.getCanvas().style.cursor = 'crosshair';
                    } else {
                        map.getCanvas().style.cursor = 'default';
                    }
                };
            },
        });

        window.bop = new App();
    });
});
