// This is the js for the default/index.html view.

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
        self.vue.courses = [];

      // Gets new courses in response to a query, or to an initial page load.
      $.getJSON(courses_url, function(data) {
          self.vue.my_courses = data.my_courses;

          self.vue.edit_course_str = data.current_url;
          self.vue.edit_course_str += self.vue.course_id;


          //self.vue.statistics_str = data.stat_url;
          //self.vue.statistics_str += self.vue.course_id;


          //enumerate(self.vue.my_courses);
          //self.vue.admin = data.admin;
          self.vue.loading = false;

      });
    };



    self.get_projects = function () {
      self.vue.loading = true;
      self.vue.projects = [];
      // Gets new products in response to a query, or to an initial page load.
      $.getJSON(projects_url, $.param({c_id: self.vue.course_id}), function(data) {
          self.vue.edit_project_str = data.current_url;
          self.vue.edit_project_str += "/" + self.vue.course_id;


          // console.log(data.current_url);
          // console.log(self.vue.edit_project_str);
          self.vue.projects = data.projects;
          self.vue.admin = data.student;
          //enumerate(self.vue.projects);
          self.vue.loading = false;
      });
    };

    self.get_members = function(){
        // console.log("XFILES");
        $.getJSON(members_url, $.param({c_id: self.vue.course_id}), function(data){
            self.vue.my_members = data.members;
        });
        // console.log("FUX")
    };

    self.get_one_project = function (course_id,p_id) {
      self.vue.course_id = course_id;
      self.vue.project_id = p_id;
      self.vue.loading = true;
      self.vue.proj = [];
      self.vue.proj_matches = [];
      // Gets new products in response to a query, or to an initial page load.
      $.getJSON(view_project_url, $.param({c_id: self.vue.course_id, p_id: self.vue.project_id}), function(data) {
          self.vue.proj = data.project;
          self.vue.proj_matches = data.matches;
          //enumerate(self.vue.proj);
          //enumerate(self.vue.proj_matches);
          self.vue.loading = false;
      });
    };

    self.get_one_course = function(course_id){

        self.vue.course_id = course_id;
        self.vue.course=[];
        self.vue.course_members=[];
        self.vue.projects_in_course = [];
        self.vue.not_in_projects=[];
      $.getJSON(view_statistics_url, $.param({c_id: self.vue.course_id}), function(data){

        self.vue.course = data.course;
        self.vue.course_members = data.course_members;
        self.vue.projects_in_course = data.projects;
        self.vue.not_in_projects = data.not_in_projects;
      });
        //
        // console.log( "at end of js function : ", self.vue.course_id);
        // console.log("at end of js function:", self.vue.course);
        // console.log("at end of js function:", self.vue.course_members);
        // console.log("at end of js function: ", self.vue.projects_in_course);
        // console.log("at end of js function: ", self.vue.not_in_projects);

    };






    self.goto = function (page, course_id, p_id) {
        self.vue.page = page;
        self.vue.course_id = course_id;
        self.vue.project_id = p_id;
        self.vue.current_course = course_id;
        if (page == 'project_list') {
          // Get the orders if the current page is order_hist
          self.get_projects();
        };
        if (page == 'courses') {
          self.get_courses();
        };
        if (page == 'members'){
            self.get_members();
        };
    };

    self.get_dashboard = function () {
        $.getJSON(current_url, function(data){
            self.vue.current = data.current_user;
        });
        self.vue.projects = [];
        self.get_courses();
    };


    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            loading: false,
            my_courses: [],
            projects: [],
            courses: [],
            projects_in_course: [],
            proj_matches: [],
            proj: [],
            course: [],
            course_members: [],
            my_members: [],
            not_in_projects: [],
            coursework: [],
            current: "",
            course_name: "",
            course_id: "",
            project_id: "",
            form: "",
            page: 'courses',
            current_course: null,
            edit_project_str: "",
            edit_course_str: "",
            statistics_str:"",
            course_name:"",
        },
        methods: {
            get_dashboard: self.get_dashboard,
            get_courses: self.get_courses,
            get_one_course: self.get_one_course,
            get_projects: self.get_projects,
            get_one_project: self.get_one_project,
            get_members: self.get_members,
            //edit_project: self.edit_project,
            //send_project: self.send_project,
            goto: self.goto,
        }

    });

    self.get_dashboard();
    //self.read_cart();
    $("#vue-div").show();


    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
