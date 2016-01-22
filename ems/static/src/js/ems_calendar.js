openerp.ems = function (instance) {
    instance.web_calendar.CalendarView = instance.web_calendar.CalendarView.extend({
        event_data_transform: function (event) {
            var res = this._super.apply(this, arguments);

            //var match = /^.+?(?: \[([0-9]+)\])?$/g;
            //var color = match.exec(event.color[1])[1];
            var color = event.color;

            //self.get_color(event.id)
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
                                    //var pattern = /^(.+?)(?: \[([0-9]+)\])?$/g;
                                    //var match = pattern.exec(val[1]);
                                    //var label = match[1];
                                    //var color = match[2];
                                    var label = val[1];
                                    /var color = val[0];
                                    if (!color) {
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