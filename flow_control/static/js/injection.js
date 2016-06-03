
var settings = {
  timeToCheck: 1,
  tabTogo: null,
  defaulTabId:null,
  defaultAction: 1,
  targetUrl:null,
  targetId:null,
  lmsBaseJumpUrl:"../../../jump_to_id/",
  message:null,
  conditionReached: null,
  inStudioRuntime: false
};

var actions = {
  noAct: "No action",
  redirectTab: "Redirect to tab by id, same section",
  redirectUrl: "Redirect to URL",
  redirectJump: "Redirect using jump_to_id",
  show_message: "Show a message"
};

var conditions = {
  gradeOnProblem: "Grade on certain problem",
  gradeOnSection: "Grade on certain list of problems",
  setConditionStatus: function (data){
    settings.conditionReached = data.status;
  }
};

var viewblocks = {
  seqContent: $("#seq_content"),
  hideNotAllowedOption: function (){
    $("#settings-tab > ul > li").hide();
    $("#settings-tab > ul > li").filter('[data-field-name="condition"]').show();
    $("#settings-tab > ul > li").filter('[data-field-name="action"]').show();
    $("#settings-tab > ul > li").filter('[data-field-name="operator"]').show();
    $("#settings-tab > ul > li").filter('[data-field-name="ref_value"]').show();

    switch ($("#xb-field-edit-action").val()){

      case actions["redirectTab"]:
        $("#settings-tab > ul > li").filter('[data-field-name="to"]').show();
        break;
      case actions["redirectUrl"]:
        $("#settings-tab > ul > li").filter('[data-field-name="target_url"]').show();
        break;
      case actions["redirectJump"]:
        $("#settings-tab > ul > li").filter('[data-field-name="target_id"]').show();
        break;
      case actions["show_message"]:
        $("#settings-tab > ul > li").filter('[data-field-name="message"]').show();
        break;

    }

    switch ($("#xb-field-edit-condition").val()){

      case conditions["gradeOnProblem"]:
        $("#settings-tab > ul > li").filter('[data-field-name="problem_id"]').show();
        break;
      case conditions["gradeOnSection"]:
        $("#settings-tab > ul > li").filter('[data-field-name="list_of_problems"]').show();
        break;

    }
  },
  applyFlowControl: function(condition){
    if (condition){
      switch (settings.defaultAction){
        case actions.noAct:
          break;
        case actions.redirectTab:
          viewblocks.seqContent.empty();
          window.flowControlTimeoutID = window.setTimeout(redirectToTab,
            settings.timeToCheck,
            settings.tabTogo);
          break;
        case actions.redirectUrl:
          viewblocks.seqContent.empty();
          location.href = settings.targetUrl;
          break;
        case actions.redirectJump:
          viewblocks.seqContent.empty();
          location.href = settings.targetId;
          break;
        case actions.show_message:
          viewblocks.seqContent.html(settings.message);
          break;
      }
    }
  }
};

var getActiveTab = function() {

  // Find the ID of the active vertical
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

  if (currentID === arg){
    window.clearTimeout(window.flowControlTimeoutID);

    // Fix posible errors on the .active classes
    $activeTab.parent().siblings().find(".active").removeClass("active");
  }
  else {
    var whereTo = null;
    if (settings["defaulTabId"] > last_tab_index) {
      whereTo = last_tab;
    }
    if (settings["defaulTabId"] < first_tab_index) {
      whereTo = first_tab;
    }
    if (first_tab_index <= settings["defaulTabId"] && settings["defaulTabId"] <= last_tab_index) {
      whereTo = arg;
    }

    execControl(whereTo);
    window.flowControlTimeoutID = window.setTimeout(redirectToTab, settings["timeToCheck"], whereTo);

  }
}

function FlowControlGoto(runtime, element, options) {

  // Getting settings varibales to apply flow control
  settings.tabTogo = options.default;
  settings.defaultAction = options.action;
  settings.targetUrl = options.target_url;
  settings.targetId = settings.lmsBaseJumpUrl + options.target_id;
  settings.defaulTabId = options.default_tab_id;
  settings.message = options.message;
  settings.inStudioRuntime = options.in_studio_runtime;

  var handlerUrl = runtime.handlerUrl(element, 'condition_status_handler');

  if (!settings.inStudioRuntime){
    $.ajax({
      type: "POST",
      url: handlerUrl,
      data: JSON.stringify({"": ""}),
      success: conditions.setConditionStatus,
      async: false,
    });

    if (settings.conditionReached){
      viewblocks.applyFlowControl(settings.conditionReached);
    }
  }
  else{
    $("header.xblock-header-check-point li.action-item.action-visibility").hide();
    $("header.xblock-header-check-point li.action-item.action-duplicate").hide();
  }

}

function EditFlowControl(runtime, element) {

    // Call to StudioEditableXblockMixin function in order to initialize xblock correctly
    window.StudioEditableXBlockMixin(runtime, element);

    viewblocks.hideNotAllowedOption();

    $("#xb-field-edit-action, #xb-field-edit-condition").on("change",function(){
          viewblocks.hideNotAllowedOption();
    });

}

function StudioFlowControl(runtime, element) {

  $("header.xblock-header-check-point li.action-item.action-visibility").hide();
  $("header.xblock-header-check-point li.action-item.action-duplicate").hide();


}
