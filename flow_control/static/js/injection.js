
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

var getActiveTab = function() {

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

var redirectToTab = function(arg) {

  var $activeTab = getActiveTab(),
      currentID = $activeTab.attr("id"),
      allTabs = $("#sequence-list a"),
      first_tab_index = 0,
      first_tab = "tab_" + first_tab_index,
      last_tab_index = allTabs.length - 1,
      last_tab = "tab_" + last_tab_index;

  console.log("tic " + arg + " " + currentID);

  if (currentID === arg){
    window.clearTimeout(window.flowControlTimeoutID);

    // Fix posible errors on the .active classes
    $activeTab.parent().siblings().find(".active").removeClass("active");
  }
  else {
    var whereTo = null;
    if (settings["default_tab_id"] > last_tab_index) {
      whereTo = last_tab;
    }
    if (settings["default_tab_id"] < first_tab_index) {
      whereTo = first_tab;
    }
    if (first_tab_index <= settings["default_tab_id"] && settings["default_tab_id"] <= last_tab_index) {
      whereTo = arg;
    }

    execControl(whereTo);
    window.flowControlTimeoutID = window.setTimeout(redirectToTab, settings["time_to_check"], whereTo);

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
        break;
      case actions["redirect_tab"]:
        viewblocks["seqContent"].empty();
        window.flowControlTimeoutID = window.setTimeout(redirectToTab,
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

    $("header.xblock-header-check-point li.action-item.action-visibility").hide();
    $("header.xblock-header-check-point li.action-item.action-duplicate").hide();

  }
}

function EditFlowControl(runtime, element) {

    // Call to StudioEditableXblockMixin function in order to initialize xblock correctly
    window.StudioEditableXBlockMixin(runtime, element);

    viewblocks.hideNotAllowedOption();

    $("body").on("change","#xb-field-edit-action",function(){
          viewblocks.hideNotAllowedOption();
    });
}
