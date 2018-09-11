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

                $.ajax(url, {
                    method: (form.attr('method') || (createNew ? 'POST' : 'PUT')),
                    data: record,
                    success: function () {
                        var redirectTo = '/';

                        if (form.data('redirect-to')) {
                            redirectTo = form.data('redirect-to');
                        } else if (form.attr('name')) {
                            redirectTo = '/' + form.attr('name');
                        }

                        location.href = redirectTo;
                    }.bind(this),
                    error: function (data) {
                        console.error('Form Error:', data);
                        this.showResponseError(data);
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
                        limit: parseInt(el.data('typeahead-limit') || 9),
                        source: function (query, _, asyncResults) {
                            var url = el.data('typeahead-url');
                            var field = el.data('typeahead-field');

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

                return new Handsontable($(selector).get(0), $.extend(true, {}, config, {
                    columns:    columns,
                    colHeaders: headers,
                }));
            },
        });

        var ExpeditionPlots = Stapes.subclass({
            // Rebecca Elyanow 2018

            renderExpeditionGraphs: function(actual_JSON) {
                var live_oyster_size = this.get_oyster_size_single(actual_JSON,0.0,200.0).filter(Number);
                var number_live_oysters = this.get_number_live_oysters_single(actual_JSON,0.0,50.0).filter(Number);
                var baseline_oyster_size = live_oyster_size; // TODO
                // var total_mass_substrate_shell_oysters = get_total_mass_substrate_shell_oysters(actual_JSON,2.0,1000.0);

                console.log('oyster size',live_oyster_size.sort());

                this.plot(
                    live_oyster_size,
                    0.0,
                    200.0,
                    5.0,
                    'Live oyster size (mm)',
                    'Live oyster size (mm)',
                    'Number of oysters',
                    'div_oyster_size'
                );

                this.plot_barchart(
                    [...Array(live_oyster_size.length).keys()].map(String),

                    live_oyster_size.sort(function(a, b) {
                    return a - b;
                    }),

                    Math.round(live_oyster_size.length/10),
                    10,
                    'Live oyster size (mm)',
                    'Oyster',
                    'Live oyster size (mm)',
                    'div_barplot_oyster_size'
                );

                this.plot_boxplot(
                    baseline_oyster_size,
                    live_oyster_size,
                    Math.round(live_oyster_size.length/10),
                    10,
                    'Live oyster size (mm)',
                    'Oyster',
                    'Live oyster size (mm)',
                    'div_boxplot_oyster_size'
                );

                // this.plot_dates(actual_JSON,get_oyster_size,0.0,200.0,5.0,'Live oyster size (mm)','Live oyster size (mm)','Number of oysters','div_dates_oyster_size')
                //this.plot_expeditions(actual_JSON,get_oyster_size,0.0,200.0,5.0,'Live oyster size (mm)','Live oyster size (mm)','Number of oysters','div_expeditions_oyster_size')

                this.plot(
                    number_live_oysters,
                    0.0,
                    50.0,
                    1.0,
                    'Number of live oysters',
                    'Number of live oysters',
                    'Number of substrate shells',
                    'div_number_oysters'
                );

                this.plot_barchart(
                    [...Array(number_live_oysters.length).keys()].map(String),
                    number_live_oysters,
                    1,
                    1,
                    'Number of live oysters',
                    'Substrate shell',
                    'Number of live oysters',
                    'div_barplot_number_oysters'
                );

                // this.plot_dates(actual_JSON,get_number_live_oysters,0.0,50.0,1.0,'Number of live oysters','Number of live oysters','Number of substrate shells','div_dates_number_oysters')
                // this.plot_expeditions(actual_JSON,get_number_live_oysters,0.0,50.0,1.0,'Number of live oysters','Number of live oysters','Number of substrate shells','div_expeditions_number_oysters')

                // plot(total_mass_substrate_shell_oysters,0.0,1000.0,20.0,'Total mass of substrate shell oysters (g)','Total mass of substrate shell oysters (g)','Number of substrate shells','div_mass_oysters')
                // this.plot_dates(actual_JSON,get_total_mass_substrate_shell_oysters,0.0,1000.0,20.0,'Total mass of substrate shell oysters (g)','Total mass of substrate shell oysters (g)','Normalized number of substrate shells','div_dates_mass_oysters')
                // this.plot_expeditions(actual_JSON,get_total_mass_substrate_shell_oysters,0.0,1000.0,20.0,'Total mass of substrate shell oysters (g)','Total mass of substrate shell oysters (g)','Normalized number of substrate shells','div_expeditions_mass_oysters')
            },

            concat: function(x,y) {
                return x.concat(y);
            },

            flatMap: function(f,xs) {
                return xs.map(f).reduce(this.concat,[]);
            },

            get_date: function(actual_JSON) {
                var x = actual_JSON.map(function(y) {
                    return y.collectionTime.substring(0,10).split('-').map(function(z) {
                        return parseFloat(z);
                    });
                });
                return x;
            },

            diffDates: function(first, second) {
                for (var i = 0; i < first.length; i++){
                    first[i] = first.diff(second);
                }

                return first;
            },

            get_oyster_size: function(actual_JSON,min,max){
                var x = this.flatMap(function(x) {
                    return this.flatMap(function(y) {
                        return y.measurements.map(function(z) {
                            return z.sizeOfLiveOysterMM;
                        });
                    },x.measuringOysterGrowth.substrateShells);
                }.bind(this), actual_JSON);

                //#.filter(Number);
                // x = x.filter(function(x) {
                //     return x <= max && x >= min;
                // });
                return x;
            },

            get_oyster_size_single: function(actual_JSON,min,max){
                console.log('measuringOysterGrowth',actual_JSON.protocols.oysterMeasurement.measuringOysterGrowth.substrateShells);
                var x = this.flatMap(function(y) {
                    return y.measurements.map(function(z) {
                        return z.sizeOfLiveOysterMM;
                    });
                }, actual_JSON.protocols.oysterMeasurement.measuringOysterGrowth.substrateShells);//#.filter(Number);
                // x = x.filter(function(x) {
                //     return x <= max && x >= min;
                // });
                return x;
            },

            get_means: function(actual_JSON){
                var d = this.flatMap(function(x) {
                    return this.flatMap(function(y) {
                        return y.measurements.map(function(z) {
                            return y.averageSizeOfLiveOysters;
                        });
                    },x.measuringOysterGrowth.substrateShells);
                }.bind(this), actual_JSON);

                return d;
            },

            get_size_means: function(actual_JSON){
                var x = this.flatMap(function(x) {
                    return this.flatMap(function(y) {
                        return y.measurements.map(function(z) {
                            return y.averageSizeOfLiveOysters;
                        });
                    },x.measuringOysterGrowth.substrateShells);
                }.bind(this), actual_JSON).filter(Number);
                return x;
            },

            get_number_live_oysters: function(actual_JSON,min,max){
                var x = this.flatMap(function(x) {
                    return this.flatMap(function(y) {
                        return y.totalNumberOfLiveOystersOnShell;
                    },x.measuringOysterGrowth.substrateShells);
                }.bind(this), actual_JSON).filter(Number);

                x = x.filter(function(x) {
                    return x <= max && x >= min;
                });
                return x;
            },

            get_number_live_oysters_single: function(actual_JSON,min,max){
                var x = this.flatMap(function(y) {
                    return y.totalNumberOfLiveOystersOnShell;
                }, actual_JSON.protocols.oysterMeasurement.measuringOysterGrowth.substrateShells).filter(Number);
                return x;
            },

            get_total_mass_substrate_shell_oysters: function(actual_JSON,min,max){
                var x = this.flatMap(function(x) {
                    return this.flatMap(function(y) {
                        return y.totalMassOfScrubbedSubstrateShellOystersTagG;
                    },x.measuringOysterGrowth.substrateShells);
                }.bind(this), actual_JSON).filter(Number);

                x = x.filter(function(x) {
                    return x <= max && x >= min;
                });

                return x;
            },

            plot: function(x,start,end,size,title,xaxis,yaxis,div) {
                var trace = {
                    x   : x,
                    type: 'histogram',
                    xbins: {
                        end  : end,
                        size : size,
                        start: start
                    }
                };
                var data = [trace];
                var layout = {
                    bargap   : 0.05,
                    title    : title,
                    xaxis: {
                        title: xaxis,
                    },
                    yaxis: {
                        title: yaxis,
                    },
                    width    : 700,
                    height   : 500,
                };

                Plotly.newPlot(div, data,layout);
            },

            plot_dates: function(actual_JSON,datafun,start,end,size,title,xaxis,yaxis,div) {
                var data_2016 = actual_JSON.filter(function(x) {
                    return x.collectionTime.startsWith('2016');
                });

                var data_2017 = actual_JSON.filter(function(x) {
                    return x.collectionTime.startsWith('2017');
                });

                var data_2018 = actual_JSON.filter(function(x) {
                    return x.collectionTime.startsWith('2018');
                });

                var vector_2016 = datafun(data_2016,start,end);
                var vector_2017 = datafun(data_2017,start,end);
                var vector_2018 = datafun(data_2018,start,end);
                var trace_2016 = {
                    x        : vector_2016,
                    type     : 'histogram',
                    histnorm : 'probability',
                    opacity  : 0.5,
                    name     : "2016",
                    xbins: {
                        end  : end,
                        size : size,
                        start: start
                    },
                    marker: {
                        color: 'red',
                    }
                };
                var trace_2017 = {
                    x        : vector_2017,
                    type     : 'histogram',
                    name     : "2017",
                    opacity  : 0.5,
                    xbins: {
                        end  : end,
                        size : size,
                        start: start
                    },
                    marker: {
                        color: 'blue',
                    }
                };
                var trace_2018 = {
                    x        : vector_2018,
                    type     : 'histogram',
                    name     : "2018",
                    opacity  : 0.5,
                    xbins: {
                        end  : end,
                        size : size,
                        start: start
                    },
                    marker: {
                        color: 'green',
                    }
                };

                var data = [trace_2016,trace_2017,trace_2018];

                var layout = {
                    bargap     : 0.05,
                    bargroupgap: 0.1,
                    title      : title,
                    xaxis: {
                        title  : xaxis,
                    },
                    yaxis: {
                        title  : yaxis,
                    },
                    width      : 700,
                    height     : 500,
                };

                Plotly.newPlot(div, data,layout);

            },

            plot_expeditions(actual_JSON,datafun,start,end,size,title,xaxis,yaxis,div) {
                var map = new Map();

                actual_JSON.forEach(function(x) {
                    var siteName = x.longitude + "," + x.latitude; // get ORS location from longitude and latitude
                    if(map.has(siteName)) {
                        map.get(siteName).push(x);
                    } else {
                        map.set(siteName,[x]);
                    }
                });

                var data1 = [];
                var data2 = [];

                Array.from(map.values()).forEach(function(x) {
                    if (x.length > 1){
                        var val1 = x[0];
                        var val2 = x[x.length-1];
                        data1.push(val1);
                        data2.push(val2);
                    }
                });

                var diffs = diffDates(
                    data1.map(function(v) {
                        return v.collectionTime;
                    }),

                    data2.map(function(v) {
                        return v.collectionTime;
                    })
                );

                for (var i = 0; i < diffs.length; i++) { //swap if first data is after second date
                    if (diffs[i] < 0) {
                        var d1 = data1[i];
                        var d2 = data2[i];
                        data1[i] = d2;
                        data2[i] = d1;
                        diffs[i] = Math.abs(diffs[i]);
                    }
                }

                var vector1 = datafun(data1,start,end); // get vector of data for first time point (oyster size, number of live oysters, ect.)
                var vector2 = datafun(data2,start,end); // get vector of data for last time point

                if (datafun == get_oyster_size){
                    means1 = this.get_means(data1);
                    means2 = this.get_means(data2);

                    var difference_in_size_per_month = [];

                    for (var i = 0; i < vector1.length; i++) {
                        if (vector1[i] >= 300) { // correct high values (assume off by factor of 10)
                            vector1[i] = vector1[i]/10;
                        }
                        if (vector2[i] >= 300) { // correct high values
                            vector2[i] = vector2[i]/10;
                        }
                        if (means1[i] >= 20 && vector2[i] < 10){
                            vector2[i] = vector2[i]*10; //correct low values (cm instead of mm)
                        }
                        vector1 = vector1.filter(Number);
                        vector2 = vector2.filter(Number);
                        difference_in_size_per_month.push((vector2[i] - vector1[i]) / ((diffs[0]+1) / 30));
                    }

                    console.log('diffs',diffs.length);
                    console.log('vectors',vector1.length,vector2.length);
                    console.log(difference_in_size_per_month);
                }

                var trace1 = {
                    x        : vector1,
                    type     : 'histogram',
                    opacity  : 0.5,
                    name     : "First expedition",
                    xbins: {
                        end  : end,
                        size : size,
                        start: start,
                    },
                    marker: {
                        color: 'red',
                    }
                };

                var trace2 = {
                    x        : vector2,
                    type     : 'histogram',
                    name     : "Most recent expedition",
                    opacity  : 0.5,
                    xbins: {
                        end  : end,
                        size : size,
                        start: start,
                    },
                    marker: {
                        color: 'blue',
                    },
                };

                var data = [trace1,trace2];
                var layout = {
                    bargap     : 0.05,
                    bargroupgap: 0.1,
                    title      : title,
                    xaxis      : {
                        title: xaxis,
                    },
                    yaxis      : {
                        title: yaxis,
                    },
                    width      : 700,
                    height     : 500,
                };
                Plotly.newPlot(div, data,layout);

            },


            plot_barchart: function(x,y,xtick,ytick,title,xaxis,yaxis,div){
                console.log(x,y)
                var trace1 = {
                    x     : x,
                    y     : y,
                    type  : 'bar',
                    bargap: 0.05,
                };

                var data = [trace1];
                var layout = {
                    bargap: 0.05,
                    title : title,
                    xaxis : {
                        title: xaxis,
                        dtick: xtick,
                    },
                    yaxis : {
                        title: yaxis,
                        dtick: ytick,
                    },
                    width : 700,
                    height: 500,
                };
                Plotly.newPlot(div, data,layout);
            },

            plot_boxplot: function(first,current,xtick,ytick,title,xaxis,yaxis,div){
                var trace1 = {
                    y     : first,
                    type  : 'box',
                    bargap: 0.05,
                    name  : "Baseline"
                };
                var trace2 = {
                    y     : current,
                    type  : 'box',
                    bargap: 0.05,
                    name  : "Current expedition"
                };

                var data = [trace2];
                var layout = {
                    bargap: 0.05,
                    title : title,
                    xaxis : {title: xaxis,dtick: xtick},
                    yaxis : {title: yaxis,dtick: ytick},
                    width : 700,
                    height: 500,
                };

                Plotly.newPlot(div, data,layout);
            }
        });

        window.bop = new App();
        window.expeditionPlots = new ExpeditionPlots();
    });
});