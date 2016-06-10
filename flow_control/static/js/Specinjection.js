var specMessages = {
  suiteTitle: 'Testing suite for FlowControl Xblock',
  initFlowControlConditionReached: 'When not on Studio runtime and condition reached, It should initialize Xblock correctly and call applyFlowControl',
  initFlowControlConditionNotReached: 'When not on Studio runtime and false condition, It should initialize Xblock correctly, no call to applyFlowControl',
  initFlowControlOnStudio: 'On Studio runtime, It should initialize Xblock correctly, hide ui elements',
  initEditFlowControl: 'It should initialize Xblock correctly on studio edit view and set on change event listener',
  initStudioFlowControl: 'It should initialize Xblock correctly on studio view and hide ui elements',
  viewblocks: 'Variable viewblocks.seqContent should be #seq_content',
  setCondition: 'It should set the current condition status '

};

describe(specMessages.suiteTitle, function() {
    var runtime = jasmine.createSpy();
    var element = jasmine.createSpy();
    var options = jasmine.createSpy();

    beforeEach(function() {
        options.in_studio_runtime = false;
        options.default = 'tab_0';
        options.action = 'No action';
        options.target_url = 'www.testing.com';
        options.target_id = '7t6723g4hvbhvs934';
        options.default_tab_id = 0;
        options.message = 'Message';
    });

    it(specMessages.initFlowControlConditionReached, function() {

        spyOn($, 'ajax').and.callFake(function(request) {
            data = {'success': true, 'status': true};
            request.success(data);
        });
        spyOn(viewblocks, 'applyFlowControl');
        runtime.handlerUrl = jasmine.createSpy();
        FlowControlGoto(runtime, element, options);

        expect(settings.tabTogo).toBe(options.default);
        expect(settings.defaultAction).toBe(options.action);
        expect(settings.targetUrl).toBe(options.target_url);
        expect(settings.targetId).toBe(settings.lmsBaseJumpUrl + options.target_id);
        expect(settings.defaulTabId).toBe(options.default_tab_id);
        expect(settings.message).toBe(options.message);
        expect(viewblocks.applyFlowControl).toHaveBeenCalledWith(true);
        expect($.ajax).toHaveBeenCalledTimes(1);

    });

    it(specMessages.initFlowControlConditionNotReached, function() {

        spyOn($, 'ajax').and.callFake(function(request) {
            var data = {'success': true, 'status': false};
            request.success(data);
        });
        spyOn(viewblocks, 'applyFlowControl');
        runtime.handlerUrl = jasmine.createSpy();
        FlowControlGoto(runtime, element, options);

        expect(settings.tabTogo).toBe(options.default);
        expect(settings.defaultAction).toBe(options.action);
        expect(settings.targetUrl).toBe(options.target_url);
        expect(settings.targetId).toBe(settings.lmsBaseJumpUrl + options.target_id);
        expect(settings.defaulTabId).toBe(options.default_tab_id);
        expect(settings.message).toBe(options.message);
        expect(viewblocks.applyFlowControl).not.toHaveBeenCalled();
        expect($.ajax).toHaveBeenCalledTimes(1);

    });

    it(specMessages.initFlowControlOnStudio, function() {

        options.in_studio_runtime = true;
        var hideSpy = spyOn($.fn, 'hide');
        runtime.handlerUrl = jasmine.createSpy();
        FlowControlGoto(runtime, element, options);
        uiElementsHided = hideSpy.calls.all();

        expect(uiElementsHided[0].object.selector).toBe(uiSelectors.visibility);
        expect(uiElementsHided[1].object.selector).toBe(uiSelectors.duplicate);
        expect(hideSpy).toHaveBeenCalledTimes(2);
        expect(settings.tabTogo).toBe(options.default);
        expect(settings.defaultAction).toBe(options.action);
        expect(settings.targetUrl).toBe(options.target_url);
        expect(settings.targetId).toBe(settings.lmsBaseJumpUrl + options.target_id);
        expect(settings.defaulTabId).toBe(options.default_tab_id);
        expect(settings.message).toBe(options.message);

    });


    it(specMessages.initEditFlowControl, function() {

        spyOn(viewblocks, "hideNotAllowedOption");
        window['StudioEditableXBlockMixin'] = jasmine.createSpy();
        spyOn($.fn, 'on');

        EditFlowControl(runtime,element);

        expect($.fn.on).toHaveBeenCalledTimes(1);
        expect(window.StudioEditableXBlockMixin).toHaveBeenCalled();
        expect(viewblocks.hideNotAllowedOption).toHaveBeenCalled();

    });

    it(specMessages.initStudioFlowControl, function() {

        var hideSpy = spyOn($.fn, 'hide');
        StudioFlowControl(runtime,element);
        uiElementsHided = hideSpy.calls.all();

        expect(uiElementsHided[0].object.selector).toBe(uiSelectors.visibility);
        expect(uiElementsHided[1].object.selector).toBe(uiSelectors.duplicate);
        expect(hideSpy).toHaveBeenCalledTimes(2);

    });

    it(specMessages.viewblocks, function() {

        expect(viewblocks.seqContent).toEqual($("#seq_content"));

    });

    it(specMessages.setCondition, function() {

        var data = {'success': true, 'status': false};
        conditions.setConditionStatus(data);

        expect(settings.conditionReached).toBe(data.status);

    });

});