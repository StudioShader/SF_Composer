$(document).ready(function() {
    const projects = JSON.parse(document.getElementsById("projects_data").textContent);
    console.log(projects);
    console.log("something");
    for (let project in projects){
      $("#project"+project.id).on( "click", function(id=project.id) {
        $('#project_iframe').attr('src', "/LODesigner/lo_designer/"+id);
        for (let project in projects){
          $('#project' + project.id).removeClass("active");
        }
        $('#project' + id).addClass("active");
      });
    }
  })