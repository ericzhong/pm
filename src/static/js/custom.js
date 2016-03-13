/**
 * checkboxes for edit roles
 */

// show checkboxlist in table
$("a[name='btn-show-checkboxlist']").click( function() {
  url = $(this).attr('data-href');
  td = $(this).closest('tr').find("td[data-toggle='checkboxlist_form']");
  $.getJSON( url, function( data ) {
    f = $('#checkboxlist_form').clone().show().removeAttr('id').attr('action', url);
    c = f.find("div[name='content']");
    $.each( data.all, function( key, item ) {
      if( 0 > $.inArray( item.id, data.selected) && 0 > $.inArray( item.id, data.disabled ) ) {
        var checked = "";
      }else{
        var checked = "checked";
      }
      if( 0 > $.inArray( item.id, data.disabled ) ) {
        var disabled = "";
      }else {
        var disabled = "disabled";
      }
      c.append("<div><input name='item' type='checkbox' value='"+ item.id +"'" + checked + ' ' + disabled +"> "+ item.name +"</div>");
    });
    td.children().hide();
    td.append(f);
  });
});

// hide checkboxlist in table
$("button[name='btn-hide-checkboxlist']").live('click', function() {
  td = $(this).closest('tr').find("td[data-toggle='checkboxlist_form']");
  td.children().show();
  $(this).closest('td').find('form').remove();    // prevent click "edit" repeated
  return false;
});

// select one at least
$("td[data-toggle='checkboxlist_form'] input:checkbox").live('change', function(){
  var form = $(this).closest("form");
  var len = form.find("input:checkbox:checked").length;
  var btn = form.find("button:submit[name='submit']");
  (len == 0)? btn.prop('disabled', true) : btn.prop('disabled', false);
});


/**
 * tab active
 */

$('li#'+$('#admin-tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#project-tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#settings-tab-content').attr('tab-toggle')).attr('class', 'active');


/**
 * confirm delete
 */

$('#confirm-delete').on('show.bs.modal', function(e) {
  $(e.target).find('form').attr('action', $(e.relatedTarget).attr('data-href'));
  // v-align center
  $(e.target).css('padding-top', $(document).height()/2-200);
});


/**
 * datepicker
 */

$.fn.datepicker.defaults.format = "yyyy-mm-dd";
$.fn.datepicker.defaults.autoclose = true;

$('.date-picker').datepicker().on('changeDate', function(selected){
  var start_date = $(this).attr("start-date");
  var end_date = $(this).attr("end-date");
  var show_date = $(this).attr("show-date");
  var date = new Date(selected.date.valueOf());

  if (show_date) $('#' + show_date).val($(this).data('datepicker').getFormattedDate($.fn.datepicker.defaults.format));
  if (start_date) $('#' + start_date).datepicker('setEndDate', date);
  if (end_date) $('#' + end_date).datepicker('setStartDate', date);
});

// initial value
(function(){
  $('.date-picker').each(function(){
    var start_date = $(this).attr("start-date");
    var end_date = $(this).attr("end-date");
    var show_date = $(this).attr("show-date");

    var date = null;
    if (show_date)
      date = $('#' + show_date).val();
    else
      date = $(this).val();

    if (end_date && date) $('#' + end_date).datepicker('setStartDate', new Date(date));
    if (start_date && date) $('#' + start_date).datepicker('setEndDate', new Date(date));
  });
})();
