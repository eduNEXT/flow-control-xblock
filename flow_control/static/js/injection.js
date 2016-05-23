console.log("Flow-Control Injected");

var settings = {
  time_to_check: 1,
  tab_togo: null,
  default_action: 1,
  target_url:null
};

var actions = {
  no_act: "No action",
  redirect_tab: "Redirect to tab, same section",
  redirect_url: "Redirect to URL",
  redirect_jump_to: "Redirecti using JumpTo",
  show_message: "Show a message"
};

var TIMEOUT = 1;
var moduleElement;
var tab_togo;
var default_action;


var getActiveTab = function(element) {

  // Find the ID of the active vertical
  // var activeVerticalID = $(element).closest(".xblock-student_view-vertical").data("usage-id");
  var activeVerticalID = $("#course-content #seq_content .xblock-student_view-vertical").data("usage-id");

  // Get the tab from the sequence that points to this vertical
  var $tab = $('#sequence-list a').filter(function() {
    return $(this).data("id") == activeVerticalID;
  });

  return $tab
}

var execControl = function(arg) {
  // Find the target tab
  var $target = $('#sequence-list a').filter(function() {
    return $(this).attr("id") == arg;
  });

  // Do the action
  $target.click();

  // TODO: can we make this silent. E.g. that it does not post to /handler/xmodule_handler/goto_position
}

var someTimedOutFunction = function(arg) {

  var $activeTab = getActiveTab(moduleElement);  // Que pasa si no encuentra un active tab?
  var currentID = $activeTab.attr("id");

  console.log("tic " + arg + " " + currentID);

  if (currentID === arg){
    console.log("clearTimeout");
    window.clearTimeout(window.flowControlTimeoutID);

    // Fix posible errors on the .active classes
    $activeTab.parent().siblings().find(".active").removeClass("active");
  }
  else {
    execControl(arg);

    console.log("setTimeout");
    window.flowControlTimeoutID = window.setTimeout(someTimedOutFunction, TIMEOUT, arg);
  }
}

function FlowControlGoto(runtime, element, options) {
  //console.log("Running FlowControlGoto ", options);
  settings["tab_togo"] = options.default
  settings["default_action"] = options.action;
  settings["target_url"] = options.target_url;

  //console.log("tab default", settings["tab_togo"]);
  console.log("default action", settings["default_action"]);
  //console.log(element);
  
  var targetId = options.target || 'tab_3';

  //Getting xblock runtime environment element
  var runtime = $("[data-block-type='check-point']");

  //Only apply flow control on LMS runtime
  if (runtime.data("runtime-class") === "LmsRuntime") {
    switch (settings["default_action"]){
      case actions["no_act"]:
        console.log("no action needed, see render content");
        break;
      case actions["redirect_tab"]:
        execControl(targetId);
        window.flowControlTimeoutID = window.setTimeout(someTimedOutFunction, TIMEOUT, settings["tab_togo"]);
        break;
      case actions["redirect_url"]:
        console.log("toUrl");
        window.location.replace(settings["target_url"]);
        break;
      case actions["redirect_jump_to"]:
        console.log("jumpTo");
        break;
      case actions["show_message"]:
        console.log("showMessage");
        break;
    }  
  }
  
}
