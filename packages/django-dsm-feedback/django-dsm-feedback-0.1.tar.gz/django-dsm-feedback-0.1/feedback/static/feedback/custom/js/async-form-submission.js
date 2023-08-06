
document.addEventListener('DOMContentLoaded', function(){
  // grab all widget icons
  var icons = document.querySelectorAll("feedback-widget img.icon")

  // for each icon, bind click to change icon and input value
  icons.forEach(function(e, i){
    e.onclick = function() {
      $('feedback-widget img.icon.active').toggleClass('active', false)
      $(e).toggleClass('active', true)
      $("#feedback-form-rating").val(i)
    }
  })

  // show / hide email part of form when may-we-contact-you is toggled.
  $("#may-we-contact-you").change(function() {
    $("#may-we-contact-you").is(':checked')
    ? $("#feedback-email-container").show().prop('required', true)
    : $("#feedback-email-container").hide().prop('required', false)
  })


  // when feedback form is submitted
  $("#feedback-form").submit(function(e){
    // intercept default behavior
    e.preventDefault()

    // async ajax request
    $.ajax({
      data: $(this).serialize(),
      type: $(this).attr('method'),
      url: $(this).attr('action'),
      success: function(response){
        console.log(response)
      },
      error: function(data){
        console.log(data)
      }
    })
  })

  // when submit button is clicked, submit form
  $("#feedback-form-submit-button").click(function(){
    $("#feedback-form-page").val(window.location.pathname)
    var form = $("#feedback-form")
    form.submit()
    $("#feedback-modal").modal('hide')

    $("#feedback-modal").remove()
    $("#feedback-tab").remove()
    $(".modal-backdrop").remove()

  })


  $("#feedback-modal").on('show.bs.modal', function(){
    var path = window.location.pathname
    var bcs = path.split('/')
    bcs[0] = 'home'
    // bcs.splice(-1,1)

    $("#feedback-breadcrumbs li").remove()

    bcs.forEach(function(e, i){
      $("#feedback-breadcrumbs").append(
        '<li class="breadcrumb-item '+(i == bcs.length - 1 ? 'active" aria-current="page"' : '"')+'><a>'+e+'</a></li>'
      )
    })
  })

})
