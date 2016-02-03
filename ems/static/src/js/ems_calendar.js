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
                    _.each(this.fields_view.arch.children, function(o) {
                        if (o.attrs.invisible === "1") {
                             delete temp_ret[o.attrs.name]
                        }
                    });

                    var res_text= [];
                    _.each(temp_ret, function(val,key) {
                        if( typeof(val) == 'boolean' && val == false ) { }
                        else {
                            if (!isNullOrUndef(val)) {
                                res_text.push(val);
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
                    var color;
                    if (!isNullOrUndef(self.fields[this.color_field].related)) {
                        color = evt[this.color_field];
                    } else {
                        color = this.get_color(color_key);
                    }
                    r.className = 'cal_opacity calendar_color_'+ color;
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
                                        var rel_field = e[color_field.related[0]];
                                        label = rel_field[1];
                                        if (isNullOrUndef(val)) {
                                            color = self.get_color(rel_field[0])
                                        } else {
                                             color = val[0];
                                        }
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
        }
    });
};