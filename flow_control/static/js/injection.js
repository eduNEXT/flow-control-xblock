console.log("Flow-Control Injected");

var TIMEOUT = 1;
var moduleElement;
var tab_togo;


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
  console.log("Running FlowControlGoto ", options);
  tab_togo = options.default

  console.log("tab default", tab_togo);
  
  var targetId = options.target || 'tab_3';

  execControl(targetId);
  window.flowControlTimeoutID = window.setTimeout(someTimedOutFunction, TIMEOUT, tab_togo);

  $(function ($) {
        
  });

}
