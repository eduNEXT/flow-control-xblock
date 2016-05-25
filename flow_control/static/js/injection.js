console.log("Flow-Control Injected");

var settings = {
  time_to_check: 1,
  tab_togo: null,
  default_tab_id:null,
  default_action: 1,
  target_url:null,
  target_id:null,
  lms_base_jump_url:"../../../jump_to_id/",
  message:null
};

var actions = {
  no_act: "No action",
  redirect_tab: "Redirect to tab by id, same section",
  redirect_url: "Redirect to URL",
  redirect_jump: "Redirect using jump_to_id",
  show_message: "Show a message"
};

var viewblocks = {
  seqContent: $("#seq_content"),
  hideNotAllowedOption: function (){
    $("#settings-tab > ul > li").filter('[data-field-name!="action"]').hide()
    
    switch ($("#xb-field-edit-action").val()){

      case actions["redirect_tab"]:
        $("#settings-tab > ul > li").filter('[data-field-name="to"]').show()
        break;
      case actions["redirect_url"]:
        $("#settings-tab > ul > li").filter('[data-field-name="target_url"]').show()
        break;
      case actions["redirect_jump"]:
        $("#settings-tab > ul > li").filter('[data-field-name="target_id"]').show()
        break;
      case actions["show_message"]:
        $("#settings-tab > ul > li").filter('[data-field-name="message"]').show()
        break;
      
    }  
  
  }
};

var moduleElement;

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

  //console.log("tic " + arg + " " + currentID);
  var allTabs =$("div[id^='seq_contents_']");

  if (currentID === arg){
    console.log("clearTimeout");
    window.clearTimeout(window.flowControlTimeoutID);

    // Fix posible errors on the .active classes
    $activeTab.parent().siblings().find(".active").removeClass("active");
  }
  else {
    execControl(arg);
    console.log("setTimeout");
    window.flowControlTimeoutID = window.setTimeout(someTimedOutFunction, settings["time_to_check"], arg);

  }
}

function FlowControlGoto(runtime, element, options) {

  settings["tab_togo"] = options.default
  settings["default_action"] = options.action;
  settings["target_url"] = options.target_url;
  settings["target_id"] = settings["lms_base_jump_url"] + options.target_id;
  settings["default_tab_id"] = options.default_tab_id;
  settings["message"] = options.message;
  //var targetId = options.target;

  //Getting xblock runtime environment element
  var runtime = $("[data-block-type='check-point']");

  //Only apply flow control actions on LMS runtime
  if (runtime.data("runtime-class") === "LmsRuntime") {
    
    switch (settings["default_action"]){
      case actions["no_act"]:
        console.log("no action needed");
        break;
      case actions["redirect_tab"]:
        //execControl(targetId);
        viewblocks["seqContent"].empty();
        window.flowControlTimeoutID = window.setTimeout(someTimedOutFunction, 
                                        settings["time_to_check"], 
                                        settings["tab_togo"]);
        break;
      case actions["redirect_url"]:
        viewblocks["seqContent"].empty();
        location.href = settings["target_url"];
        break;
      case actions["redirect_jump"]:
        viewblocks["seqContent"].empty();
        location.href = settings["target_id"];
        break;
      case actions["show_message"]:
        viewblocks["seqContent"].html(settings["message"]);
        break;
    }  
  }

  if (runtime.data("runtime-class") === "PreviewRuntime") {
    
    $("body").on("change","#xb-field-edit-action",function(){
          viewblocks.hideNotAllowedOption();
    });
    
  }
  
}
