
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


// tab selected
$('li#'+$('#tab-content').attr('tab-toggle')).attr('class', 'active');
$('li#'+$('#settings-tab-content').attr('tab-toggle')).attr('class', 'active');