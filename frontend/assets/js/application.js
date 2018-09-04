'use strict';

// return whether the input is null OR undefined
window.isEmpty = function (v) {
    if (v === null || v === undefined) {
        return true;
    }

    return false;
};

window.qs = function() {
    var queries = {};

    $.each(document.location.search.substr(1).split('&'),function(c,q){
        var i = q.split('=', 2);

        if (i.length == 2) {
            queries[i[0].toString()] = i[1].toString();
        }
    });

    return queries;
};

window.validatePositive = function(checkvalue) {
    return function(value, callback){
        try {
            if ($.isNumeric(value) && checkvalue(value)) {
                callback(true);
                return;
            }
        } catch(e) {
            ;
        }

        callback(false);
    }
};

$(function () {
    Raven.config('https://5f7fe95584dc40f8adfd06ead1d1748c@sentry.io/1199998').install();

    Raven.context(function () {
        var App = Stapes.subclass({
            constructor: function () {
                this.setupHandsontable();
                this.setupAjaxIntercept();
                this.setupFormIntercept();
                this.setupTypeaheadHandlers();
                this.updateActiveMenuItem();

                if (location.host.indexOf('localhost') === 0) {
                    this.expandProcessStep();
                    this.handleCollapseEvents();
                }

                // handle button toggles
                this.handleToggleButtons();
                this.syncToggleButtonStates();

            },

            // setup collapse event handlers
            handleCollapseEvents: function() {
                $(window).on('shown.bs.collapse', function(e) {
                    var target = $(e.target);
                    var id = e.target.id;

                    if (id) {
                        if ($('[data-target="#' + id + '"]').hasClass('process-step')) {
                            var q = qs();

                            q.step = id;
                            history.pushState(null, null, location.pathname + '?' + $.param(q));
                        }
                    }
                }.bind(this));
            },

            expandProcessStep: function() {
                var q = qs();

                if (q.step) {
                    $('#' + q.step).collapse('show');
                }
            },

            // turns "btn-group-toggle" elements into a kind of radio button
            handleToggleButtons: function () {
                $('.btn-group-toggle input').on('click', function(e) {
                    var input = $(e.target);

                    if (input.length) {
                        var toggle = input.closest('.btn-group-toggle');

                        if (toggle.length) {
                            if (input.attr('value') && input.attr('name')) {
                                toggle.attr('data-field-value', input.attr('value'));
                                this.syncToggleButtonStates();
                            }
                        }
                    }
                }.bind(this));
            },

            syncToggleButtonStates: function() {
                $('.btn-group-toggle[data-field-value]').each(function(i, e) {
                    var toggle = $(e);
                    var value = toggle.attr('data-field-value');

                    if (toggle.length && value.length) {
                        var input = toggle.find('input[value="' + value + '"]');

                        toggle.find('.btn').removeClass('active');
                        input.closest('.btn').addClass('active');
                    }
                }.bind(this));
            },

            setupAjaxIntercept: function () {
                $(document).ajaxError(function (e, res, xhr) {
                    Raven.captureMessage('HTTP ' + res.status, {
                        'level': 'warning',
                        'extra': {
                            'status': res.status,
                            'payload': (res.responseJSON || res.responseText),
                            'request': xhr,
                        },
                    });
                });
            },

            setupFormIntercept: function () {
                // prevent normal form submissions, we'll handle them here
                $('form').on('submit', function (e) {
                    try {
                        var st = $(e.currentTarget).attr('data-form-type');

                        if (st === 'traditional' || st === 'custom') {
                            return;
                        }

                        this.submitForm(e);
                    } catch (e) {
                        this.notify('Form Error: ' + e.message, 'error');
                    }

                    e.preventDefault();
                }.bind(this));
            },

            submitForm: function (event) {
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

                $.each(form.serializeArray(), function (i, field) {
                    if (field.value == '' || field.value == '0') {
                        delete field['value'];
                    }

                    if (field.name == "_id") {
                        if (field.value) {
                            createNew = false;
                        }

                        record['_id'] = field.value;
                    } else if (!isEmpty(field.value)) {
                        record[field.name] = field.value;
                    }
                });

                form.find('[data-has-table]').each(function(i, el) {
                    el = $(el);
                    var hot = el.data('table');

                    if (hot) {
                        record[el.attr('data-field-name')] = hot.getData();
                    }
                });

                console.debug('Submitting', record)

                $.ajax(url, {
                    method: (form.attr('method') || (createNew ? 'POST' : 'PUT')),
                    data:  JSON.stringify(record),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        var redirectTo = '/';

                        if (form.attr('data-debug-log') === 'true') {
                            console.debug(data)
                            return;

                        } else if (form.attr('data-redirect-to')) {
                            redirectTo = form.attr('data-redirect-to');
                        } else if (form.attr('name')) {
                            redirectTo = '/' + form.attr('name');
                        }

                        location.href = redirectTo;
                    }.bind(this),
                    error: function (data) {
                        console.error('Form Error:', data.responseJSON.error);
                    }.bind(this),
                })
            },

            // show a notification alert bubble
            notify: function (message, type, details, config) {
                $.notify($.extend(details, {
                    'message': message,
                }), $.extend(config, {
                    'type': (type || 'info'),
                }));
            },

            // show a notification bubble for response errors
            showResponseError: function (response) {
                this.notify(response.responseText, 'danger', {
                    'icon': 'fa fa-warning',
                    'title': '<b>' +
                        response.statusText + ' (HTTP ' + response.status.toString() + ')' +
                        '<br />' +
                        '</b>',
                });
            },

            setupTypeaheadHandlers: function () {
                // setup typeahead for fields that have it
                $('.typeahead').each(function (i, el) {
                    el = $(el);

                    el.typeahead({
                        highlight: true,
                        async: true,
                    }, {
                        limit: parseInt(el.attr('data-typeahead-limit') || 9),
                        source: function (query, _, asyncResults) {
                            var url = el.attr('data-typeahead-url');
                            var field = el.attr('data-typeahead-field');

                            if (url) {
                                url = url.replace(/\{\}/g, query.replace(/^\//, ''));

                                $.ajax(url, {
                                    success: function (data) {
                                        if (field) {
                                            var results = [];
                                            var fieldNames = field.split(',');

                                            $.each(data, function (i, value) {
                                                if ($.isPlainObject(value)) {
                                                    var parts = [];

                                                    $.each(fieldNames, function(j, fname) {
                                                        if (value[fname]) {
                                                            parts.push(value[fname]);
                                                        }
                                                    });

                                                    results.push(parts.join(', '));
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

            genericMapClickHandler: function (map, layers) {
                return function (e) {
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

                        var currentPopup = new mapboxgl.Popup({
                                offset: [0, -15]
                            })
                            .setLngLat(feature.geometry.coordinates)
                            .setHTML('<p>' + feature.properties.description + '</p>')
                            .setLngLat(feature.geometry.coordinates)
                            .addTo(map);
                    } catch (e) {;
                    }
                }
            },

            genericMapHoverHandler: function (map, layers) {
                return function (e) {
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

            updateActiveMenuItem: function () {
                var pathComponents = window.location.pathname.split('/');

                $("[data-menu-triggers] .dropdown-menu").removeClass('show');
                $("[data-menu-triggers]").removeClass('show');

                if (pathComponents.length > 1) {
                    var expandSelector = "[data-menu-triggers~='" + pathComponents[1] + "']";

                    $(expandSelector + ' .dropdown-menu').addClass('show');
                    $(expandSelector).addClass('show');
                }
            },

            setupHandsontable: function() {
                Handsontable.validators.registerValidator('valid-settlement-tile', validatePositive(function(v){
                    return (v > 0) && (v <= 10) && Math.floor(v) == v;
                }));

                Handsontable.validators.registerValidator('valid-oyster', validatePositive(function(v) {
                    return (v > 0) && (v < 250);
                }));

                Handsontable.validators.registerValidator('valid-species-count', validatePositive(function(v) {
                    return (v >= 0);
                }));
            },

            createTable: function(selector, headers, columns, config) {
                var el = $(selector);

                config = $.extend(true, {}, {
                    stretchH:            'all',
                    autoWrapRow:         true,
                    minSpareRows:        5,
                    startRows:           5,
                    maxRows:             100,
                    manualRowResize:     true,
                    manualColumnResize:  true,
                    contextMenu:         false,
                    rowHeaders:          true,
                    preventOverflow:     'horizontal',
                    currentRowClassName: 'current-row',
                    currentColClassName: 'current-col',
                }, (config || {}));

                el.data('table', new Handsontable(el.get(0), $.extend(true, {}, config, {
                    columns:    columns,
                    colHeaders: headers,
                })));

                el.attr('data-has-table', 'true');

                return el.data('table');
            },
        });

        window.bop = new App();
    });
});