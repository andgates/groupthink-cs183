// This is the js for the default/my_courses.html view.

var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) {
        var k=0;
        return v.map(function(e) {e._idx = k++;});
    };

    self.get_courses = function () {
      self.vue.loading = true;
      // Gets new products in response to a query, or to an initial page load.
      $.getJSON(courses_url, function(data) {
          self.vue.my_courses = data.my_courses;
          enumerate(self.vue.my_courses);
          self.vue.loading = false;
          console.log(self.vue.my_courses);
      });
    };

/*
    self.get_projects = function () {
      self.vue.loading = true;
      // Gets new products in response to a query, or to an initial page load.
      $.getJSON(projects_url, $.param({q: self.vue.product_search}), function(data) {
          self.vue.my_courses = data.my_courses;
          enumerate(self.vue.my_courses);
          self.vue.loading = false;
          console.log(self.vue.my_courses);
      });
    };
*/

    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            loading: false,
            my_courses: [],
        },
        methods: {
            get_courses: self.get_courses,
        }

    });

    self.get_courses();
    //self.read_cart();
    $("#vue-div").show();


    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
