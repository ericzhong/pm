
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


// tab active
$('li#'+$('#admin-tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#project-tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#settings-tab-content').attr('tab-toggle')).attr('class', 'active');


// confirm delete
$('#confirm-delete').on('show.bs.modal', function(e) {
  $(e.target).find('form').attr('action', $(e.relatedTarget).attr('data-href'));
  // v-align center
  $(e.target).css('padding-top', $(document).height()/2-200);
});


/**
 * datepicker
 */

$('.date-picker.start-date').find("button").datepicker({
  autoclose: true,
}).on('changeDate', function(selected){
  date = new Date(selected.date.valueOf());
  $(this).closest('.date-picker').find('input').val($(this).data('datepicker').getFormattedDate('yyyy-mm-dd'));
  $('.date-picker.end-date').find('button').datepicker('setStartDate', date);
});

$('.date-picker.end-date').find("button").datepicker({
  autoclose: true
}).on('changeDate', function(selected){
  date = new Date(selected.date.valueOf());
  $(this).closest('.date-picker').find('input').val($(this).data('datepicker').getFormattedDate('yyyy-mm-dd'));
  $('.date-picker.start-date').find('button').datepicker('setEndDate', date);
});

$('.date-picker').find("button").datepicker({
  autoclose: true,
}).on('changeDate', function(selected){
  $(this).closest('.date-picker').find('input').val($(this).data('datepicker').getFormattedDate('yyyy-mm-dd'));
});
