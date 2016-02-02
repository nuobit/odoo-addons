openerp.ems = function (instance) {
    var QWeb = instance.web.qweb;

    function isNullOrUndef(value) {
        return _.isUndefined(value) || _.isNull(value);
    }

    instance.web_calendar.CalendarView = instance.web_calendar.CalendarView.extend({
        /*
        event_data_transform: function (event) {
            var res = this._super.apply(this, arguments);
            var color = event.color;

            if (color) {
                res.className = res.className.replace(/calendar_color_[0-9]+/g, "calendar_color_" + color);
                res.title = res.title.replace(new RegExp(' \\['+color+'\\]$'), '');
            }

            var title0 = res.title.split(",");
            var title9 = [];
            _.each(title0, function(value, key) {
                if (value.trim().length!=0) {
                    title9.push(value.trim());
                }

            });
            res.title = title9.join(", ");

            return res;
        },
        */
        event_data_transform: function(evt) {
            var self = this;

            var date_delay = evt[this.date_delay] || 1.0,
                all_day = this.all_day ? evt[this.all_day] : false,
                res_computed_text = '',
                the_title = '',
                attendees = [];

            if (!all_day) {
                date_start = instance.web.auto_str_to_date(evt[this.date_start]);
                date_stop = this.date_stop ? instance.web.auto_str_to_date(evt[this.date_stop]) : null;
            }
            else {
                date_start = instance.web.auto_str_to_date(evt[this.date_start].split(' ')[0],'start');
                date_stop = this.date_stop ? instance.web.auto_str_to_date(evt[this.date_stop].split(' ')[0],'start') : null; //.addSeconds(-1) : null;
            }

            if (this.info_fields) {
                var temp_ret = {};
                res_computed_text = this.how_display_event;

                _.each(this.info_fields, function (fieldname) {
                    var value = evt[fieldname];
                    if (_.contains(["many2one", "one2one"], self.fields[fieldname].type)) {
                        if (value === false) {
                            temp_ret[fieldname] = null;
                        }
                        else if (value instanceof Array) {
                            temp_ret[fieldname] = value[1]; // no name_get to make
                        }
                        else {
                            throw new Error("Incomplete data received from dataset for record " + evt.id);
                        }
                    }
                    else if (_.contains(["one2many","many2many"], self.fields[fieldname].type)) {
                        if (value === false) {
                            temp_ret[fieldname] = null;
                        }
                        else if (value instanceof Array)  {
                            temp_ret[fieldname] = value; // if x2many, keep all id !
                        }
                        else {
                            throw new Error("Incomplete data received from dataset for record " + evt.id);
                        }
                    }
                    else if (_.contains(["date", "datetime"], self.fields[fieldname].type)) {
                        temp_ret[fieldname] = instance.web.format_value(value, self.fields[fieldname]);
                    }
                    else {
                        temp_ret[fieldname] = value;
                    }
                    res_computed_text = res_computed_text.replace("["+fieldname+"]",temp_ret[fieldname]);
                });


                if (res_computed_text.length) {
                    the_title = res_computed_text;
                }
                else {
                    var res_text= [];
                    _.each(this.invisible_fields, function(fieldname) {
                        delete temp_ret[fieldname]
                    });

                    _.each(temp_ret, function(val,key) {
                        if( typeof(val) == 'boolean' && val == false ) { }
                        else {
                            if (!isNullOrUndef(val)) {
                                res_text.push(val)
                            }
                        };
                    });
                    the_title = res_text.join(', ');
                }
                the_title = _.escape(the_title);


                the_title_avatar = '';

                if (! _.isUndefined(this.attendee_people)) {
                    var MAX_ATTENDEES = 3;
                    var attendee_showed = 0;
                    var attendee_other = '';

                    _.each(temp_ret[this.attendee_people],
                        function (the_attendee_people) {
                            attendees.push(the_attendee_people);
                            attendee_showed += 1;
                            if (attendee_showed<= MAX_ATTENDEES) {
                                if (self.avatar_model !== null) {
                                       the_title_avatar += '<img title="' + _.escape(self.all_attendees[the_attendee_people]) + '" class="attendee_head"  \
                                                            src="/web/binary/image?model=' + self.avatar_model + '&field=image_small&id=' + the_attendee_people + '"></img>';
                                }
                                else {
                                    if (!self.colorIsAttendee || the_attendee_people != temp_ret[self.color_field]) {
                                            tempColor = (self.all_filters[the_attendee_people] !== undefined)
                                                        ? self.all_filters[the_attendee_people].color
                                                        : (self.all_filters[-1] ? self.all_filters[-1].color : 1);
                                        the_title_avatar += '<i class="fa fa-user attendee_head color_'+tempColor+'" title="' + _.escape(self.all_attendees[the_attendee_people]) + '" ></i>';
                                    }//else don't add myself
                                }
                            }
                            else {
                                attendee_other += _.escape(self.all_attendees[the_attendee_people]) +", ";
                            }
                        }
                    );
                    if (attendee_other.length>2) {
                        the_title_avatar += '<span class="attendee_head" title="' + attendee_other.slice(0, -2) + '">+</span>';
                    }
                    the_title = the_title_avatar + the_title;
                }
            }

            if (!date_stop && date_delay) {
                date_stop = date_start.clone().addHours(date_delay);
            }
            var r = {
                'start': date_start.toString('yyyy-MM-dd HH:mm:ss'),
                'end': date_stop.toString('yyyy-MM-dd HH:mm:ss'),
                'title': the_title,
                'allDay': (this.fields[this.date_start].type == 'date' || (this.all_day && evt[this.all_day]) || false),
                'id': evt.id,
                'attendees':attendees
            };
            if (!self.useContacts || self.all_filters[evt[this.color_field]] !== undefined) {
                if (this.color_field && evt[this.color_field]) {
                    var color_key = evt[this.color_field];
                    if (typeof color_key === "object") {
                        color_key = color_key[0];
                    }
                    //r.className = 'cal_opacity calendar_color_'+ this.get_color(color_key);
                    r.className = 'cal_opacity calendar_color_'+ evt.color;
                }
            }
            else  { // if form all, get color -1
                  r.className = 'cal_opacity calendar_color_'+ self.all_filters[-1].color;
            }
            return r;
        },

        do_search: function(domain, context, _group_by) {
           var self = this;
           if (! self.all_filters) {
                self.all_filters = {}
           }

            if (! _.isUndefined(this.event_source)) {
                this.$calendar.fullCalendar('removeEventSource', this.event_source);
            }
            this.event_source = {
                events: function(start, end, callback) {
                    var current_event_source = self.event_source;
                    self.dataset.read_slice(_.keys(self.fields), {
                        offset: 0,
                        domain: self.get_range_domain(domain, start, end),
                        context: context
                    }).done(function(events) {
                        if (self.dataset.index === null) {
                            if (events.length) {
                                self.dataset.index = 0;
                            }
                        } else if (self.dataset.index >= events.length) {
                            self.dataset.index = events.length ? 0 : null;
                        }

                        if (self.event_source !== current_event_source) {
                            console.log("Consecutive ``do_search`` called. Cancelling.");
                            return;
                        }

                        if (!self.useContacts) {  // If we use all peoples displayed in the current month as filter in sidebars
                            var filter_item;

                            self.now_filter_ids = [];

                            var color_field = self.fields[self.color_field];
                            _.each(events, function (e) {
                                var key,val = null;
                                if (color_field.type == "selection") {
                                    key = e[self.color_field];
                                    val = _.find(color_field.selection, function(name){ return name[0] === key;});
                                }
                                else {
                                    key = e[self.color_field][0];
                                    val = e[self.color_field];
                                }
                                if (!self.all_filters[key]) {
                                    var label, color;
                                    if (!isNullOrUndef(color_field.related)) {
                                        label = e[color_field.related[0]][1];
                                        color = val[0];
                                    } else {
                                        label = val[1]
                                        color = self.get_color(key);
                                    }
                                    filter_item = {
                                        value: key,
                                        label: label,
                                        color: color,
                                        avatar_model: (_.str.toBoolElse(self.avatar_filter, true) ? self.avatar_filter : false ),
                                        is_checked: true
                                    };
                                    self.all_filters[key] = filter_item;
                                }
                                if (! _.contains(self.now_filter_ids, key)) {
                                    self.now_filter_ids.push(key);
                                }
                            });

                            if (self.sidebar) {
                                self.sidebar.filter.events_loaded();
                                self.sidebar.filter.set_filters();

                                events = $.map(events, function (e) {
                                    var key = color_field.type == "selection" ? e[self.color_field] : e[self.color_field][0];
                                    if (_.contains(self.now_filter_ids, key) &&  self.all_filters[key].is_checked) {
                                        return e;
                                    }
                                    return null;
                                });
                            }

                        }
                        else { //WE USE CONTACT
                            if (self.attendee_people !== undefined) {
                                //if we don't filter on 'Everybody's Calendar
                                if (!self.all_filters[-1] || !self.all_filters[-1].is_checked) {
                                    var checked_filter = $.map(self.all_filters, function(o) { if (o.is_checked) { return o.value; }});
                                    // If we filter on contacts... we keep only events from coworkers
                                    events = $.map(events, function (e) {
                                        if (_.intersection(checked_filter,e[self.attendee_people]).length) {
                                            return e;
                                        }
                                        return null;
                                    });
                                }
                            }
                        }
                        var all_attendees = $.map(events, function (e) { return e[self.attendee_people]; });
                        all_attendees = _.chain(all_attendees).flatten().uniq().value();

                        self.all_attendees = {};
                        if (self.avatar_title !== null) {
                            new instance.web.Model(self.avatar_title).query(["name"]).filter([["id", "in", all_attendees]]).all().then(function(result) {
                                _.each(result, function(item) {
                                    self.all_attendees[item.id] = item.name;
                                });
                            }).done(function() {
                                return self.perform_necessary_name_gets(events).then(callback);
                            });
                        }
                        else {
                            _.each(all_attendees,function(item){
                                    self.all_attendees[item] = '';
                            });
                            return self.perform_necessary_name_gets(events).then(callback);
                        }
                    });
                },
                eventDataTransform: function (event) {
                    return self.event_data_transform(event);
                }
            };
            this.$calendar.fullCalendar('addEventSource', this.event_source);
        },

        view_loading: function (fv) {
            /* xml view calendar options */
            var attrs = fv.arch.attrs,
                self = this;
            this.fields_view = fv;
            this.$calendar = this.$el.find(".oe_calendar_widget");

            this.info_fields = [];
            this.invisible_fields = [];

            /* buttons */
            this.$buttons = $(QWeb.render("CalendarView.buttons", {'widget': this}));
            if (this.options.$buttons) {
                this.$buttons.appendTo(this.options.$buttons);
            } else {
                this.$el.find('.oe_calendar_buttons').replaceWith(this.$buttons);
            }

            this.$buttons.on('click', 'button.oe_calendar_button_new', function () {
                self.dataset.index = null;
                self.do_switch_view('form');
            });

            if (!attrs.date_start) {
                throw new Error(_t("Calendar view has not defined 'date_start' attribute."));
            }

            this.$el.addClass(attrs['class']);

            this.name = fv.name || attrs.string;
            this.view_id = fv.view_id;

            this.mode = attrs.mode;                 // one of month, week or day
            this.date_start = attrs.date_start;     // Field name of starting date field
            this.date_delay = attrs.date_delay;     // duration
            this.date_stop = attrs.date_stop;
            this.all_day = attrs.all_day;
            this.how_display_event = '';
            this.attendee_people = attrs.attendee;

            if (!isNullOrUndef(attrs.quick_create_instance)) {
                self.quick_create_instance = 'instance.' + attrs.quick_create_instance;
            }

            //if quick_add = False, we don't allow quick_add
            //if quick_add = not specified in view, we use the default quick_create_instance
            //if quick_add = is NOT False and IS specified in view, we this one for quick_create_instance'

            this.quick_add_pop = (isNullOrUndef(attrs.quick_add) || _.str.toBoolElse(attrs.quick_add, true));
            if (this.quick_add_pop && !isNullOrUndef(attrs.quick_add)) {
                self.quick_create_instance = 'instance.' + attrs.quick_add;
            }
            // The display format which will be used to display the event where fields are between "[" and "]"
            if (!isNullOrUndef(attrs.display)) {
                this.how_display_event = attrs.display; // String with [FIELD]
            }

            // If this field is set ot true, we don't open the event in form view, but in a popup with the view_id passed by this parameter
            if (isNullOrUndef(attrs.event_open_popup) || !_.str.toBoolElse(attrs.event_open_popup, true)) {
                this.open_popup_action = false;
            } else {
                this.open_popup_action = attrs.event_open_popup;
            }
            // If this field is set to true, we will use the calendar_friends model as filter and not the color field.
            this.useContacts = (!isNullOrUndef(attrs.use_contacts) && _.str.toBool(attrs.use_contacts)) && (!isNullOrUndef(self.options.$sidebar));

            // If this field is set ot true, we don't add itself as an attendee when we use attendee_people to add each attendee icon on an event
            // The color is the color of the attendee, so don't need to show again that it will be present
            this.colorIsAttendee = (!(isNullOrUndef(attrs.color_is_attendee) || !_.str.toBoolElse(attrs.color_is_attendee, true))) && (!isNullOrUndef(self.options.$sidebar));

            // if we have not sidebar, (eg: Dashboard), we don't use the filter "coworkers"
            if (isNullOrUndef(self.options.$sidebar)) {
                this.useContacts = false;
                this.colorIsAttendee = false;
                this.attendee_people = undefined;
            }

/*
            Will be more logic to do it in futur, but see below to stay Retro-compatible

            if (isNull(attrs.avatar_model)) {
                this.avatar_model = 'res.partner';
            }
            else {
                if (attrs.avatar_model == 'False') {
                    this.avatar_model = null;
                }
                else {
                    this.avatar_model = attrs.avatar_model;
                }
            }
*/
            if (isNullOrUndef(attrs.avatar_model)) {
                this.avatar_model = null;
            } else {
                this.avatar_model = attrs.avatar_model;
            }

            if (isNullOrUndef(attrs.avatar_title)) {
                this.avatar_title = this.avatar_model;
            } else {
                this.avatar_title = attrs.avatar_title;
            }

            if (isNullOrUndef(attrs.avatar_filter)) {
                this.avatar_filter = this.avatar_model;
            } else {
                this.avatar_filter = attrs.avatar_filter;
            }

            this.color_field = attrs.color;

            if (this.color_field && this.selected_filters.length === 0) {
                var default_filter;
                if ((default_filter = this.dataset.context['calendar_default_' + this.color_field])) {
                    this.selected_filters.push(default_filter + '');
                }
            }

            this.fields = fv.fields;

            for (var fld = 0; fld < fv.arch.children.length; fld++) {
                this.info_fields.push(fv.arch.children[fld].attrs.name);
                if (fv.arch.children[fld].attrs.invisible==1) {
                    this.invisible_fields.push(fv.arch.children[fld].attrs.name);
                }
            }

            var edit_check = new instance.web.Model(this.dataset.model)
                .call("check_access_rights", ["write", false])
                .then(function (write_right) {
                    self.write_right = write_right;
                });
            var init = new instance.web.Model(this.dataset.model)
                .call("check_access_rights", ["create", false])
                .then(function (create_right) {
                    self.create_right = create_right;
                    self.init_calendar().then(function() {
                        $(window).trigger('resize');
                        self.trigger('calendar_view_loaded', fv);
                        self.ready.resolve();
                    });
                });
            return $.when(edit_check, init);
        }
    });
};