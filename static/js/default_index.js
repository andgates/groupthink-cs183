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
          if (self.vue.course_id != undefined) {
            self.vue.edit_course_str += self.vue.course_id;
          };
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
          self.vue.profiles_url = data.profiles_url;
          self.vue.projects = data.projects;
          self.vue.admin = data.student;
          self.vue.loading = false;
      });
    };

    self.get_members = function(){
        $.getJSON(members_url, $.param({c_id: self.vue.course_id}), function(data){
            self.vue.my_members = data.members;
            self.vue.profile_url = data.profile_url;
        });
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
          self.vue.profile_url = data.profile_url;
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
        self.vue.projects_in_course = data.projects_in_course;
        self.vue.not_in_projects = data.not_in_projects;
      });
    };






    self.goto = function (page, course_id, p_id) {
        self.vue.page = page;
        self.vue.course_id = course_id;
        self.vue.project_id = p_id;
        self.vue.current_course = course_id;
        if (page == 'project_list') {
          self.get_projects();
        };
        if (page == 'courses') {
          self.get_courses();
        };
        if (page == 'members'){
            self.get_members();
        };
    };

    self.go_to_profile = function (username) {
        self.vue.profile_url = URL('deafault', 'profile', args=[username]);
    }

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
            profile_url: "",
            profiles_url: "",
            edit_project_str: "",
            edit_course_str: "",
            statistics_str:"",
            course_name:"",
        },
        methods: {
            get_dashboard: self.get_dashboard,
            go_to_profile: self.go_to_profile,
            get_courses: self.get_courses,
            get_one_course: self.get_one_course,
            get_projects: self.get_projects,
            get_one_project: self.get_one_project,
            get_members: self.get_members,
            goto: self.goto,
        }

    });

    self.get_dashboard();
    $("#vue-div").show();


    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
