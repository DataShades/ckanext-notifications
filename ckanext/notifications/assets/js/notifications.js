document.addEventListener("DOMContentLoaded", function() {
  // Clean target properties inside content frame modules
  var snippets = document.querySelectorAll('.noti-body-snippet');
  snippets.forEach(function(box) {
    var anchors = box.querySelectorAll('a');
    anchors.forEach(function(a) {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
    });
  });

  var masterSelect = document.getElementById('select-all-notifications');
  var checkboxes = document.querySelectorAll('.notification-checkbox');
  var countDisplay = document.getElementById('selected-count');

  // Re-calculate active row metrics dynamically
  function updateSelectedCount() {
    var checkedCount = document.querySelectorAll('.notification-checkbox:checked').length;
    if (countDisplay) {
      countDisplay.textContent = checkedCount;
    }
    
    // Keep master toggle visually synchronized if rows are checked manually
    if (masterSelect) {
      masterSelect.checked = (checkedCount === checkboxes.length && checkboxes.length > 0);
    }
  }

  // Selection Toggle Handling logic matching structural state mutations
  if (masterSelect) {
    masterSelect.addEventListener('change', function() {
      checkboxes.forEach(function(cb) {
        cb.checked = masterSelect.checked;
      });
      updateSelectedCount();
    });
  }

  // Bind event listeners to each row checkbox element
  checkboxes.forEach(function(cb) {
    cb.addEventListener('change', function() {
      updateSelectedCount();
    });
  });
});

function submitBulkForm(actionKey) {
  var form = document.getElementById('bulk-action-form');
  if (!form) {
    return;
  }
  document.getElementById('bulk_action_type').value = actionKey;
  form.method = 'POST';
  form.submit();
}

function submitFilterOrderForm() {
  var form = document.getElementById('bulk-action-form');
  var filterSelect = document.getElementById('type');
  var sortSelect = document.getElementById('sort');
  var filterInput = document.getElementById('filter_type_input');
  var sortInput = document.getElementById('sort_order_input');
  var pageInput = document.getElementById('page_input');

  if (!form) {
    return;
  }

  if (filterInput && filterSelect) {
    filterInput.value = filterSelect.value;
  }
  if (sortInput && sortSelect) {
    sortInput.value = sortSelect.value;
  }
  if (pageInput) {
    pageInput.value = '1';
  }

  var checkboxes = document.querySelectorAll('.notification-checkbox');
  checkboxes.forEach(function(cb) {
    cb.disabled = true;
  });

  form.method = 'GET';
  form.submit();
}

// Submits bulk selection forms
function submitBulkAction(actionKey) {
  var activeChecked = document.querySelectorAll('.notification-checkbox:checked');
  if (activeChecked.length === 0) {
    alert('Please select at least one notification.');
    return;
  }
  if (actionKey === 'delete' && !confirm('Do you really want to delete the selected notifications?')) {
    return;
  }
  submitBulkForm(actionKey);
}

// Handles inline individual item triggers instantly by adjusting inputs programmatically
function executeSingleRowAction(notificationId, actionKey) {
  if (actionKey === 'delete' && !confirm('Do you really want to delete this notification?')) {
    return;
  }
  
  // Clear out any user checklist evaluations to process exclusively this ID
  var checkboxes = document.querySelectorAll('.notification-checkbox');
  checkboxes.forEach(function(cb) {
    cb.checked = false;
  });
  
  // Target the single target row checkbox element contextually
  var targetCb = document.querySelector('.notification-checkbox[value="' + notificationId + '"]');
  if (targetCb) {
    targetCb.checked = true;
    submitBulkForm(actionKey);
  }
}
