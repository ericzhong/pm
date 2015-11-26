
// show editor in table
$("a[name='btn-edit']").click( function() {
  td = $(this).closest('tr').children('td').eq(1);
  td.children('span').eq(0).hide();
  td.children('form').eq(0).show();
});

// hide editor in table
$("button[name='btn-cancel']").click( function() {
  td = $(this).closest('tr').children('td').eq(1);
  td.children('span').eq(0).show();
  td.children('form').eq(0).hide();
  return false;
});


// tab active
$('li#'+$('#tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#settings-tab-content').attr('tab-toggle')).attr('class', 'active');


// confirm delete
$('#confirm-delete').on('show.bs.modal', function(e) {
  $(e.target).find('form').attr('action', $(e.relatedTarget).attr('data-href'));
  // v-align center
  $(e.target).css('padding-top', $(document).height()/2-200);
});
