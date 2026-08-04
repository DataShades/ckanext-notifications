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

  // Organization and Dataset preferences interactions
  function syncDatasetChannels(datasetId, enabled) {
    var email = document.querySelector('input[name="dataset_email__' + datasetId + '"]');
    var inApp = document.querySelector('input[name="dataset_in_app__' + datasetId + '"]');
    if (email) {
      email.checked = enabled;
    }
    if (inApp) {
      inApp.checked = enabled;
    }
  }

  function syncDatasetToggleFromChannels(datasetId) {
    var datasetToggle = document.querySelector('input[name="dataset_enabled__' + datasetId + '"]');
    var email = document.querySelector('input[name="dataset_email__' + datasetId + '"]');
    var inApp = document.querySelector('input[name="dataset_in_app__' + datasetId + '"]');
    if (!datasetToggle || !email || !inApp) {
      return;
    }

    datasetToggle.checked = email.checked || inApp.checked;
  }

  function ensureOrganizationToggleEnabled(orgId) {
    if (!orgId) {
      return;
    }

    var orgToggle = document.querySelector('#notifications-organization-preferences input[name="org_enabled__' + orgId + '"]');
    if (!orgToggle || orgToggle.checked) {
      return;
    }

    orgToggle.checked = true;
    orgToggle.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function syncDatasetOrgBulkFromDatasets(orgId) {
    if (!orgId) {
      return;
    }

    var datasetCard = document.querySelector('#notifications-dataset-preferences .notifications-dataset-org-card[data-org-id="' + orgId + '"]');
    if (!datasetCard) {
      return;
    }

    var datasetToggles = datasetCard.querySelectorAll('input[name^="dataset_enabled__"]');
    var anyEnabled = false;
    datasetToggles.forEach(function(toggle) {
      if (toggle.checked) {
        anyEnabled = true;
      }
    });

    var bulkToggle = datasetCard.querySelector('.dataset-org-bulk-toggle');
    if (bulkToggle) {
      bulkToggle.checked = anyEnabled;
    }

    if (anyEnabled) {
      ensureOrganizationToggleEnabled(orgId);
    }
  }

  var datasetEnabled = document.querySelectorAll('input[name^="dataset_enabled__"]');
  datasetEnabled.forEach(function(toggle) {
    toggle.addEventListener('change', function() {
      var datasetId = toggle.name.replace('dataset_enabled__', '');
      syncDatasetChannels(datasetId, toggle.checked);
      var datasetItem = toggle.closest('.notifications-dataset-item');
      var orgId = datasetItem && datasetItem.getAttribute('data-org-id');
      syncDatasetOrgBulkFromDatasets(orgId);
    });
  });

  var datasetChannelInputs = document.querySelectorAll('input[name^="dataset_email__"], input[name^="dataset_in_app__"]');
  datasetChannelInputs.forEach(function(channelInput) {
    channelInput.addEventListener('change', function() {
      var datasetId = channelInput.name
        .replace('dataset_email__', '')
        .replace('dataset_in_app__', '');
      syncDatasetToggleFromChannels(datasetId);

      var datasetToggle = document.querySelector('input[name="dataset_enabled__' + datasetId + '"]');
      if (datasetToggle) {
        var datasetItem = datasetToggle.closest('.notifications-dataset-item');
        var orgId = datasetItem && datasetItem.getAttribute('data-org-id');
        syncDatasetOrgBulkFromDatasets(orgId);
      }
    });
  });

  datasetEnabled.forEach(function(toggle) {
    var datasetId = toggle.name.replace('dataset_enabled__', '');
    syncDatasetToggleFromChannels(datasetId);
  });

  var datasetOrgBulkToggles = document.querySelectorAll('#notifications-dataset-preferences .dataset-org-bulk-toggle');
  datasetOrgBulkToggles.forEach(function(bulkToggle) {
    bulkToggle.addEventListener('change', function() {
      var card = bulkToggle.closest('.notifications-dataset-org-card');
      if (!card) {
        return;
      }

      var datasetToggles = card.querySelectorAll('input[name^="dataset_enabled__"]');
      datasetToggles.forEach(function(datasetToggle) {
        datasetToggle.checked = bulkToggle.checked;
        var datasetId = datasetToggle.name.replace('dataset_enabled__', '');
        syncDatasetChannels(datasetId, bulkToggle.checked);
      });

      if (bulkToggle.checked) {
        ensureOrganizationToggleEnabled(card.getAttribute('data-org-id'));
      }
    });
  });

  var orgPreferencesEnabled = document.querySelectorAll('#notifications-organization-preferences input[name^="org_enabled__"]');

  function setDatasetCardState(datasetCard, enabled, clearWhenDisabling) {
    if (!datasetCard) {
      return;
    }

    var datasetBulkToggle = datasetCard.querySelector('.dataset-org-bulk-toggle');
    var datasetEnabledInputs = datasetCard.querySelectorAll('input[name^="dataset_enabled__"]');
    var datasetChannels = datasetCard.querySelectorAll('input[name^="dataset_email__"], input[name^="dataset_in_app__"]');
    var datasetPresence = datasetCard.querySelectorAll('.dataset-present-input');

    if (enabled) {
      datasetCard.style.display = '';
      if (datasetBulkToggle) {
        datasetBulkToggle.disabled = false;
      }
      datasetEnabledInputs.forEach(function(input) { input.disabled = false; });
      datasetChannels.forEach(function(input) { input.disabled = false; });
      datasetPresence.forEach(function(input) { input.disabled = false; });
      return;
    }

    datasetCard.style.display = 'none';
    if (datasetBulkToggle) {
      datasetBulkToggle.disabled = true;
      if (clearWhenDisabling) {
        datasetBulkToggle.checked = false;
      }
    }

    datasetEnabledInputs.forEach(function(input) {
      input.disabled = true;
      if (clearWhenDisabling) {
        input.checked = false;
      }
    });
    datasetChannels.forEach(function(input) {
      input.disabled = true;
      if (clearWhenDisabling) {
        input.checked = false;
      }
    });
    datasetPresence.forEach(function(input) { input.disabled = true; });
  }

  orgPreferencesEnabled.forEach(function(orgToggle) {
    orgToggle.addEventListener('change', function() {
      var orgId = orgToggle.name.replace('org_enabled__', '');
      var email = document.querySelector('#notifications-organization-preferences input[name="org_email__' + orgId + '"]');
      var inApp = document.querySelector('#notifications-organization-preferences input[name="org_in_app__' + orgId + '"]');
      var datasetCard = document.querySelector('#notifications-dataset-preferences .notifications-dataset-org-card[data-org-id="' + orgId + '"]');

      if (email) {
        email.checked = orgToggle.checked;
      }
      if (inApp) {
        inApp.checked = orgToggle.checked;
      }

      if (datasetCard) {
        setDatasetCardState(datasetCard, orgToggle.checked, !orgToggle.checked);
      }
    });
  });

  orgPreferencesEnabled.forEach(function(orgToggle) {
    var orgId = orgToggle.name.replace('org_enabled__', '');
    var datasetCard = document.querySelector('#notifications-dataset-preferences .notifications-dataset-org-card[data-org-id="' + orgId + '"]');
    setDatasetCardState(datasetCard, orgToggle.checked, false);
  });

  datasetOrgBulkToggles.forEach(function(bulkToggle) {
    var card = bulkToggle.closest('.notifications-dataset-org-card');
    if (!card) {
      return;
    }
    syncDatasetOrgBulkFromDatasets(card.getAttribute('data-org-id'));
  });

  // Turning on global notifications preference means opting out from all
  // other channels/scopes on this page.
  var preferencesForm = document.querySelector('.notifications-preferences-form');
  var globalToggle = preferencesForm && preferencesForm.querySelector('input[name="global_enabled"]');

  function getOtherPreferenceSwitches() {
    if (!preferencesForm) {
      return [];
    }

    var allSwitches = preferencesForm.querySelectorAll(
      '.notifications-switch input[type="checkbox"], .notifications-channel-badge input[type="checkbox"]'
    );

    return Array.from(allSwitches).filter(function(input) {
      return input !== globalToggle;
    });
  }

  function disableOtherPreferencesForGlobalOptOut() {
    getOtherPreferenceSwitches().forEach(function(input) {
      if (typeof input.dataset.originallyDisabled === 'undefined') {
        input.dataset.originallyDisabled = input.disabled ? 'true' : 'false';
      }

      if (!input.checked) {
        input.disabled = true;
        return;
      }

      input.checked = false;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.disabled = true;
    });
  }

  function restoreOtherPreferencesAfterGlobalOptOut() {
    getOtherPreferenceSwitches().forEach(function(input) {
      var originallyDisabled = input.dataset.originallyDisabled === 'true';
      input.disabled = originallyDisabled;
    });
  }

  if (globalToggle) {
    globalToggle.addEventListener('change', function() {
      if (globalToggle.checked) {
        disableOtherPreferencesForGlobalOptOut();
      } else {
        restoreOtherPreferencesAfterGlobalOptOut();
      }
    });

    if (globalToggle.checked) {
      disableOtherPreferencesForGlobalOptOut();
    } else {
      restoreOtherPreferencesAfterGlobalOptOut();
    }
  }
});


// Submits the bulk action form with the specified action key
function submitBulkForm(actionKey) {
  var form = document.getElementById('bulk-action-form');
  if (!form) {
    return;
  }
  document.getElementById('bulk_action_type').value = actionKey;
  form.method = 'POST';
  form.submit();
}


// Submits the filter and sort form with the current selections
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
