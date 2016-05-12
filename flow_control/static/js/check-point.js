function SomeFunctionFromXblock(runtime, element) {



  console.log("Im calling from SomeFunctionFromXblock");
  console.log("element: ", element);
  console.log("runtime: ", runtime);
  $.ajax({
      type: "POST",
      url: runtime.handlerUrl(element, 'control_point'),
      data: JSON.stringify({'json-data': 'some random data'}),
      success: function(result) {
          console.log("inside the success callback", result);
      }
  });




}
