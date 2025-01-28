
var settings = {
  defaultAction: 1,
  targetUrl: null,
  targetId: null,
  message: null,
  conditionReached: null,
  inStudioRuntime: false
};

var actions = {
  noAct: 'No action',
  redirectUrl: 'to_url',
  redirectJump: 'to_jump',
  show_message: 'display_message'
};

var conditions = {
  gradeOnProblem: 'single_problem',
  gradeOnSection: 'average_problems',
  setConditionStatus: function setConditionStatus(data) {
    settings.conditionReached = data.status;
  }
};

var nonComparableOperators = {
  allNull: 'all_null',
  allNotNull: 'all_not_null',
  hasNull: 'has_null'
};

var uiSelectors = {
  settingsFields: '#settings-tab > ul > li',
  visibility: 'header.xblock-header-flow-control li.action-item.action-visibility',
  duplicate: 'header.xblock-header-flow-control li.action-item.action-duplicate',
  action: '#xb-field-edit-action',
  condition: '#xb-field-edit-condition',
  operator: '#xb-field-edit-operator'
};

var viewblocks = {
  seqContent: $('#course-content'),
  loadingMessageHtml: "<div><p>Loading, please wait...</p></div>",
  hideNotAllowedOption: function hideNotAllowedOption() {
    $(uiSelectors.settingsFields).hide();
    $(uiSelectors.settingsFields).filter('[data-field-name="condition"]').show();
    $(uiSelectors.settingsFields).filter('[data-field-name="action"]').show();
    $(uiSelectors.settingsFields).filter('[data-field-name="operator"]').show();

    switch ($(uiSelectors.action).val()) {
    case actions.redirectUrl:
      $(uiSelectors.settingsFields).filter('[data-field-name="target_url"]').show();
      break;
    case actions.redirectJump:
      $(uiSelectors.settingsFields).filter('[data-field-name="target_id"]').show();
      break;
    case actions.show_message:
      $(uiSelectors.settingsFields).filter('[data-field-name="message"]').show();
      break;
    }

    switch ($(uiSelectors.condition).val()) {
    case conditions.gradeOnProblem:
      $(uiSelectors.settingsFields).filter('[data-field-name="problem_id"]').show();
      break;
    case conditions.gradeOnSection:
      $(uiSelectors.settingsFields).filter('[data-field-name="list_of_problems"]').show();
      break;
    }

    var specialOperators = [];
    for (var type in nonComparableOperators) {
      specialOperators.push(nonComparableOperators[type]);
    }

    if ($.inArray($(uiSelectors.operator).val(),specialOperators) == -1 ) {
      $(uiSelectors.settingsFields).filter('[data-field-name="ref_value"]').show();
    }
  },
  applyFlowControl: function applyFlowControl(condition) {
    if (condition) {
      switch (settings.defaultAction) {
      case actions.noAct:
        break;
      case actions.redirectUrl:
        viewblocks.seqContent.html(viewblocks.loadingMessageHtml);
        window.parent.location.href = settings.targetUrl;
        break;
      case actions.redirectJump:
        viewblocks.seqContent.html(viewblocks.loadingMessageHtml);
        window.parent.location.href = getJumpToIdUrl(settings.targetId);
        break;
      case actions.show_message:
        viewblocks.seqContent.html(settings.message);
        break;
      }
    }
  }
};

function FlowControlGoto(runtime, element, options) {
  // Getting settings varibales to apply flow control
  settings.defaultAction = options.action;
  settings.targetUrl = options.target_url;
  settings.targetId = options.target_id;
  settings.message = options.message;
  settings.inStudioRuntime = options.in_studio_runtime;

  var handlerUrl = runtime.handlerUrl(element, 'condition_status_handler');

  if (!settings.inStudioRuntime) {
    $.ajax({
      type: 'POST',
      url: handlerUrl,
      data: JSON.stringify({'': ''}),
      success: conditions.setConditionStatus,
      async: false
    });

    if (settings.conditionReached) {
      viewblocks.applyFlowControl(settings.conditionReached);
    }
  } else {
    $(uiSelectors.visibility).hide();
    $(uiSelectors.duplicate).hide();
  }
}

function EditFlowControl(runtime, element) {
    // Call to StudioEditableXblockMixin function in order to initialize xblock correctly
  window.StudioEditableXBlockMixin(runtime, element);

  viewblocks.hideNotAllowedOption();

  $('#xb-field-edit-action, #xb-field-edit-condition, #xb-field-edit-operator').on('change', function changeHandler() {
    viewblocks.hideNotAllowedOption();
  });
}

function StudioFlowControl(runtime, element) {
  $(uiSelectors.visibility).hide();
  $(uiSelectors.duplicate).hide();
}

function getCourseIdByUrl() {
  const regex = /(?:block-v1:)(.+)(?:\+type)/;
  const result = window.location.href.match(regex);
  if (result) {
    return result[1];
  }
  return null;
}

function getJumpToIdUrl(id) {
  return `${window.location.origin}/courses/course-v1:${getCourseIdByUrl()}/jump_to_id/${id}`;
}
