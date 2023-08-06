$(document).ready(function(){


  $('#activate_labels').select2();

  $('#toggle-label-form').click(function(e){
    e.preventDefault();
    $('#labeling-viewlet ul.activeLabels, #labeling-viewlet form').toggle();
  });
  $('#labeling-viewlet form input.closeForm').click(function(e){
    e.preventDefault();
    $('#labeling-viewlet ul.activeLabels').show();
    $('#labeling-viewlet form').hide();
  });

  $('.colorBox').click(function() {
    // reset all selected
    $(this).closest('form').find('.colorBox').removeClass('selected');
    $(this).toggleClass('selected');
    $(this).closest('form').find('input[name=color]').val($(this).data("color"));
  });

  $('.labelItem.globLabel').click(function() {
    $(this).toggleClass('selected');
    $(this).toggleClass(
      'labelcolor-' + $(this).find('.labelColor').data('color'));

    if( window.tabbedview === undefined ) {
      return;
    }

    var labels_prop;
    if (tabbedview.prop('labels')) {
      labels_prop = tabbedview.prop('labels').split(',');
    } else {
      labels_prop = [];
    }

    if($(this).hasClass('selected')) {
      labels_prop.push($(this).data('label-id'));
    } else {
      var index = labels_prop.indexOf($(this).data('label-id'));
      if(index !== -1) {
        labels_prop.splice(index, 1);
      }
    }

    tabbedview.prop('labels', labels_prop.join(','));
    // tabbedview.prop('labels', $(this).data('label-id'));
    tabbedview.reload_view();
  });

  $('.labelListing .editLabelLink').prepOverlay({
    subtype: 'ajax',
    width: '235px',
    noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');}
  });

  $('.pers-edit-1').click(function(){
    var $label = $(this)
    var $container = $label.closest('#active_url');
    var data = {'label_id': $label.data('label_id'), 'active': $label.data('active')}
    $.ajax({
      type: "POST",
      url: $container.data('obj_url') + "/pers-labeling/pers_update",
      data: data,
      cache: false,
      dataType: "json",
      success: function(result){
       if(result.ret=='ok'){
        $label.toggleClass('labelcolor-inactive labelcolor-' + $label.data('o_color'));
        $label.attr('data-active', result.new_status)
        $label.data('active', result.new_status)
       }
      }
    });
  });

});
